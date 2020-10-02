import requests


class CkanAuthApiError(Exception):
    pass


def json_from_post(*args, **kwargs):
    response = requests.post(*args, **kwargs)
    if response.status_code != 200:
        raise CkanAuthApiError(response.text)
    return response.json()


class CkanAuthApi:
    def __init__(self, api_url, api_key, organization, dataset_id):
        self.api_url = api_url
        self.api_key = api_key
        self.organization = organization
        self.dataset_id = dataset_id

    def get_jwt_from_ckan_authz(self, scope):
        """Get an authorization token from ckanext-authz-service."""
        url = f'{self.api_url}/api/3/action/authz_authorize'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': self.api_key,
        }
        return json_from_post(url, headers=headers, json={'scopes': scope})

    def do_blob_authz(self):
        """Creates the scope and send it to CKAN Authz to get a token."""
        scope = [f'obj:{self.organization}/{self.dataset_id}/*:write']
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
        url = f'{self.api_url}/{self.organization}/{self.dataset_id}/objects/batch'
        token = self.do_blob_authz()
        data = {
            'operation': 'upload',
            'transfers': ['basic'],
            'ref': {'name': 'refs/heads/contrib'},
            'objects': [
                {
                    'oid': resource['descriptor']['hash'],
                    'size': resource['size'],
                }
            ],
        }
        headers = {
            'Accept': 'application/vnd.git-lfs+json',
            'Content-Type': 'application/vnd.git-lfs+json',
            'Authorization': f'Bearer {token}',
        }
        return json_from_post(url, headers=headers, json=data)
