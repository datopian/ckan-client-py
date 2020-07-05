import logging
from urllib.parse import urljoin

import requests

log = logging.getLogger(__name__)

def get_jwt_from_ckan_authz(base_url, token, scope):
    # Get an authorization token from ckanext-authz-service

    path = '/api/3/action/authz_authorize'
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': token,
    }

    body = {'scopes': scope}
    response = requests.post(urljoin(base_url, path), body, headers)

    if response.status_code != 200:
        log.exception('Ckan Authz Server response: {}'.format(response.status_code))
        return

    return response.json()

def request_file_upload_actions(base_url, token, file_hash, file_size, organization, dataset_id):
    # Send Batch API request to Git LFS server, get upload / verify actions using the authz token

    path = "/{}/{}/objects/batch".format(organization, dataset_id)
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
        'Authorization': 'Bearer {}'.format(token),
    },

    response = requests.post(urljoin(base_url, path), body, headers)
    if response.status_code != 200:
        log.exception('Git LFS server response: {}'.format(response.status_code))
        return

    return response.json()
