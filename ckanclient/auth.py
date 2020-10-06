import requests

from ckanclient.errors import ResponseError


class CkanAuthApiError(ResponseError):
    pass


def json_from_post(*args, **kwargs):
    response = requests.post(*args, **kwargs)
    if response.status_code != 200:
        raise CkanAuthApiError(response)
    return response.json()


class CkanAuthApi:
    def __init__(self, client):
        """Expects an instance of `ckanclient.Client`."""
        self.client = client

    def get_jwt_from_ckan_authz(self, scope):
        """Get an authorization token from ckanext-authz-service."""
        url = f'{self.client.api_url}api/3/action/authz_authorize'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': self.client.api_key,
        }
        return json_from_post(url, headers=headers, json={'scopes': scope})

    def do_blob_authz(self):
        """Creates the scope and send it to CKAN Authz to get a token."""
        scope = [f'obj:{self.client.organization}/{self.client.dataset_id}/*:write']
        response = self.get_jwt_from_ckan_authz(scope)
        try:
            return response['result']['token']
        except KeyError:
            msg = (
                'Could not get s token from ckanext-authz-service. The '
                'response was expected to have a key `result` and, inside it, '
                f'a key `token`. The response was: {response}.'
            )
            raise CkanAuthApiError(msg)

    def request_file_upload_actions(self, resource):
        """Returns a signed URL, a verification URL and a JWT token."""
        path = f'{self.client.organization}/{self.client.dataset_id}/objects/batch'
        url = f'{self.client.lfs_url}{path}'
        data = {
            'operation': 'upload',
            'transfers': ['basic'],
            'ref': {'name': 'refs/heads/contrib'},
            'objects': [
                {
                    'oid': resource['stats']['hash'],
                    'size': resource['stats']['bytes'],
                }
            ],
        }
        headers = {
            'Accept': 'application/vnd.git-lfs+json',
            'Content-Type': 'application/vnd.git-lfs+json',
            'Authorization': f'Bearer {self.do_blob_authz()}',
        }
        return json_from_post(url, headers=headers, json=data)
