import logging
import json
import os
from os import listdir
from urllib.parse import urljoin
import hashlib

import requests

from ckan_sdk import f11s

log = logging.getLogger(__name__)


class Client:
    '''
    This is a class for authentiacation and uploading the
    data to the CKAN and cloud storage

    Attributes:
        base_url (str): url to the server
        auth_token (str): authetication token for the request
        organization_id (str): name of the organization
    '''

    def __init__(self, base_url, auth_token, organization_id):
        self.base_url = base_url
        self.auth_token = auth_token
        self.organization_id = organization_id

    def push(self, dataset, append=False):
        '''
        This function is to push the resource/resources to ckan
        and cloud.
        It also creates dataset to the ckan (if apeend=False)
        within the oraganization that is passed to the constructor.

        Parameters:
        dataset (object): object of a f11s.Dataset class.
        append (boolean): by default it is set to False means
                        not appending the resource to already
                        present dataset.

        Returns:
        list of dict: contains oid, size, success, file_already_exists
            and dataset keys and their values.
        '''

        dataset = dataset.descriptor
        dataset['owner_org'] = self.organization_id
        if not dataset.get('resources'):
            dataset = self._ckan_package_or_resource_create(dataset, 'api/3/action/package_create')['result']
            log.info('There is no resource in the dataset')
            return
        else:
            resources = dataset.pop('resources')

        if not append:
            dataset = self._ckan_package_or_resource_create(dataset, 'api/3/action/package_create')['result']
        else:
            resources = [resources[-1]]

        res = []
        for resource in resources:
            resource['package_id'] = dataset['id']

            # Get the JWT token from CkanAuthz
            scope = 'obj:{}/{}/*:write'.format(self.organization_id, dataset.get('name'))
            response = self.get_jwt_from_ckan_authz(scope)
            jwt_token = response['result']['token']

            lfs_response = self.request_file_upload_actions(jwt_token,
                                resource.get('hash'), resource.get('size'),
                                dataset.get('name'))

            lfs_object = lfs_response.get('objects')[0]
            result = {
                'oid': lfs_object['oid'],
                'size': lfs_object['size'],
                'success': False,
                'file_already_exists': False,
                'dataset': dataset.get('id')
                }

            # File doesn't exist in storage
            if lfs_object['actions']:

                # Upload the file to cloud storage
                actions = lfs_object['actions']
                upload_url = actions['upload']['href']
                upload_token = actions['upload']['header']
                self.upload_to_storage(upload_url, upload_token, resource.get('path'))

                # Verify file to cloud storage
                verify_url = actions['verify']['href']
                verify_token = actions['verify']['header']
                if self.verify_upload(verify_url, verify_token, resource.get('hash'), resource.get('size')):
                    result['success'] = True
                    resource = self._ckan_package_or_resource_create(resource, 'api/3/action/resource_create')['result']

            # File is already in storage
            else:
                result['file_already_exists'] == True
            res.append(result)

        return res

    def push_resource(self, resource_path, dataset_name, append=True):
        '''
        This function is to push a single resource to ckan
        and cloud.

        Parameters:
        resource_path (str): path to the file.
        dataset_name (str): name of the dataset.
        append (boolean): by default "True" means to append
                        resource file to existing dataset.

        Returns:
        list of dict: contains oid, size, success, file_already_exists
            and dataset keys and their values.
        '''

        dataset = self._get_ckan_dataset(dataset_name)['result']
        resource = f11s.load(resource_path)
        dataset = f11s.Dataset(dataset)
        dataset.add_resource(resource)

        return self.push(dataset, append)

    def get_jwt_from_ckan_authz(self, scope):
        '''
        This function is to get the JWT auth token
        from ckan-authz.

        Parameters:
        scope (str): scope for the token.

        Returns:
        dict: contains the json response of the request.
        '''

        path = '/api/3/action/authz_authorize'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': self.auth_token,
        }

        body = {'scopes': scope}
        url = urljoin(self.base_url, path)
        response = self.__make_ckan_post_request(url, body, headers)

        if response.status_code != 200:
            log.exception('Ckan Authz Server response: {}'.format(response.status_code))
            return

        return response.json()

    def request_file_upload_actions(self, jwt_auth_token, file_hash, file_size, dataset):
        '''
        This function is to send a batch request
        to the lfs with JWT token.

        Parameters:
        jwt_auth_token (str): Jwt token from ckan-authz.
        file_hash (str): sha256 has of the file.
        file_size (str): size of the file in bytes.
        dataset (str): name of the dataset.

        Returns:
        dict: contains the json response of the request.
        '''

        path = "/{}/{}/objects/batch".format(self.organization, dataset)
        body = {
                'operation': 'upload',
                'transfers': ['basic'],
                'ref': { 'name': 'refs/heads/contrib' },
                'objects': [
                    {
                    'oid': file_hash,
                    'size': file_size,
                    },
                ],
            }

        headers = {
            'Accept': 'application/vnd.git-lfs+json',
            'Content-Type': 'application/vnd.git-lfs+json',
            'Authorization': 'Bearer {}'.format(jwt_auth_token),
        },

        url = urljoin(self.base_url, path)
        response = self.__make_ckan_post_request(url, body, headers)
        if response.status_code != 200:
            log.exception('Git LFS server response: {}'.format(response.status_code))
            return

        return response.json()

    def upload_to_storage(self, upload_url, upload_token, file_path):
        '''
        This function is to send a batch request
        to the lfs with JWT token.

        Parameters:
        upload_url (str): upload url got from the lfs batch request.
        upload_token (str): upload token got from the lfs batch request.
        file_path (str): path of the file.

        Returns:
        dict: contains the json response of the request.
        '''

        body = open(file_path).read()
        headers ={
            'Authorization': upload_token,
        }

        response = self.__make_ckan_put_request(upload_url, body, headers)
        if response.status_code != 201:
            log.exception("Uploading the file to storage failed response: {}".format(response.status_code))
            return

        return True

    def verify_upload(self, verify_url, verify_token, file_sha256, file_size):
        '''
        This function is to send a batch request
        to the lfs with JWT token.

        Parameters:
        verify_url (str): verify url got from the lfs batch request.
        verify_token (str): verify token got from the lfs batch request.
        file_sha256 (str): sha256 hash of the file.
        file_size (str): size of the file.

        Returns:
        dict: contains the json response of the request.
        '''

        body = json.dumps({
                'oid': file_sha256,
                'size': file_size,
            })
        headers = {
            'Accept': 'application/vnd.git-lfs+json',
            'Content-Type': 'application/vnd.git-lfs+json',
            'Authorization': verify_token,
        }

        response = self.__make_ckan_post_request(verify_url, body, headers)
        if response.status_code != 200:
            log.exception("Failed to verify upload response: {}".format(response.status_code))
            return

        return True

    def __make_ckan_post_request(self, url, body, headers):
        return requests.post(url, body, headers=headers)

    def __make_ckan_put_request(self, url, body, headers):
        return requests.put(url, body, headers=headers)

    def __make_ckan_get_request(self, url, body, headers):
        return requests.get(url, body, headers=headers)

    def _ckan_package_or_resource_create(self, data, api):
        # create package or resource in the ckan instance

        url = urljoin(self.base_url, api)
        headers = {'Authorization': self.auth_token}

        response = self.__make_ckan_post_request(url, data, headers)
        if response.status_code != 200:
            log.exception("Failed to create {} in CKAN: {}".format(data['name'], response.json()['error']))
            return
        return response.json()

    def _get_ckan_dataset(self, dataset_name):
        # get package from the ckan instance

        url = urljoin(self.base_url, 'api/3/action/package_show')
        headers = {'Authorization': self.auth_token}
        params = {'id': dataset_name}

        response = self.__make_ckan_get_request(url, params, headers)
        if response.status_code != 200:
            log.exception("Failed to create a dataset to CKAN")
            return
        return response.json()
