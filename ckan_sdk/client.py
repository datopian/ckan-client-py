import logging
import json
import os
from urllib.parse import urljoin

import hashlib
import requests

log = logging.getLogger(__name__)


class Client:
    '''
    This is a class for authentiacation and uploading the
    data to the cloud storage

    Attributes:
        base_url (str): url to the server
        auth_token (str): authetication token for the request
        organization_id (str): name of the organization
        dataset_id (str): name of the dataset
    '''

    def __init__(self, base_url, auth_token, organization_id, dataset_id):
        self.base_url = base_url
        self.auth_token = auth_token
        self.organization_id = organization_id
        self.dataset_id = dataset_id

    def push(self, resource_path, on_progress=None):
        # Given the JWT token and file size, will return signed URL, verify URL and JWT token

        # Get the JWT token from CkanAuthz
        scope = 'obj:{}/{}/*:write'.format(self.organization_id, self.dataset_id)
        response = self.get_jwt_from_ckan_authz(scope)
        jwt_token = response['result']['token']

        file_info = self.get_file_info(resource_path)
        lfs_response = self.request_file_upload_actions(jwt_token,
                             file_info.get('sha256'), file_info.get('size'))

        lfs_object = lfs_response.get('objects')[0]
        result = {
            'oid': lfs_object['oid'],
            'size': lfs_object['size'],
            'name': file_info.get('name'),
            'success': True,
            'file_already_exists': False,
            }

        # File doesn't exist in storage
        if lfs_object['actions']:

            # Upload the file to cloud storage
            actions = lfs_object['actions']
            upload_url = actions['upload']['href']
            upload_token = actions['upload']['header']
            self.upload_to_storage(upload_url, upload_token, file_info.get('content'), on_progress)

            # Verify file to cloud storage
            verify_url = actions['verify']['href']
            verify_token = actions['verify']['header']
            self.verify_upload(verify_url, verify_token, file_info.get('sha256'), file_info.get('size'))

            return result

        # File is already in storage
        else:
            result['file_already_exists'] == True

    def get_jwt_from_ckan_authz(self, scope):
        # Get an authorization token from ckanext-authz-service

        path = '/api/3/action/authz_authorize'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': self.auth_token,
        }

        body = {'scopes': scope}
        url = urljoin(self.base_url, path)
        response = self._make_ckan_post_request(url, body, headers)

        if response.status_code != 200:
            log.exception('Ckan Authz Server response: {}'.format(response.status_code))
            return

        return response.json()

    def request_file_upload_actions(self, jwt_auth_token, file_hash, file_size):
        # Send Batch API request to Git LFS server, get upload / verify actions using the authz token

        path = "/{}/{}/objects/batch".format(self.organization_id , self.dataset_id)
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
        response = self._make_ckan_post_request(url, body, headers)
        if response.status_code != 200:
            log.exception('Git LFS server response: {}'.format(response.status_code))
            return

        return response.json()


    def upload_to_storage(self, upload_url, upload_token, file_content, on_progress):
        # Send a POST request with specific payload to the URL given by the Batch API response

        body = file_content
        headers ={
            'Authorization': upload_token,
        }

        if on_progress:
            headers['on_upload_progress'] = on_progress

        response = self._make_ckan_put_request(upload_url, body, headers)
        if response.status_code != 201:
            log.exception("Uploading the file to storage failed response: {}".format(response.status_code))
            return

        return True

    def verify_upload(self, verify_url, verify_token, file_sha256, file_size):
        # Get request to the verify URL given by the Batch API response

        body = json.dumps({
                'oid': file_sha256,
                'size': file_size,
            })
        headers = {
            'Accept': 'application/vnd.git-lfs+json',
            'Content-Type': 'application/vnd.git-lfs+json',
            'Authorization': verify_token,
        }

        response = self._make_ckan_post_request(verify_url, body, headers)
        if response.status_code != 200:
            log.exception("Failed to verify upload reponse: {}".format(response.status_code))
            return

        return True

    def get_file_info(self, file_path):
        # Return a dict with info of the file

        file_info = {}
        file_info['name'] = os.path.basename(file_path)

        stat_obj = os.stat(file_path)
        file_info['size'] = stat_obj.st_size

        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as file:
            file_info['content'] = file.read()

            for block in iter(lambda: file.read(50000), b''):
                sha256.update(block)

            file_info['sha256'] = sha256.hexdigest()

        return file_info

    def _make_ckan_post_request(self, url, body, headers):
        return requests.post(url, body, headers)

    def _make_ckan_put_request(self, url, body, headers):
        return requests.put(url, body, headers)