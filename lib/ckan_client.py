from .util import ckan_auth_api
from .util import ckan_upload_api
from .file import FileSystem


class Uploader:
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

    def ckan_authz(self):
        # Get the JWT token from CkanAuthz

        scope = 'obj:{}/{}/*:write'.format(self.organization_id, self.dataset_id)
        response = ckan_auth_api.get_jwt_from_ckan_authz(self.base_url, self.auth_token, scope)
        return response

    def push(self, file, token, on_progress=None):
        # Given the JWT token and file size, will return signed URL, verify URL and JWT token

        lfs_response = ckan_auth_api.request_file_upload_actions(self.base_url, token,
                             file.get_sha256(), file.get_size(), self.organization_id, self.dataset_id)

        lfs_object = lfs_response.get('objects')[0]
        result = {
            'oid': lfs_object['oid'],
            'size': lfs_object['size'],
            'name': file.get_name(),
            'success': True,
            'file_already_exists': False,
            }
        import pdb; pdb.set_trace()
        # File doesn't exist in storage
        if lfs_object['actions']:

            # Upload the file to cloud storage
            actions = lfs_object['actions']
            url = actions['upload']['href']
            token = actions['upload']['header']
            ckan_upload_api.upload_to_storage(url, token, file.get_content(), on_progress)

            # Upload the file to cloud storage
            url = actions['verify']['href']
            token = actions['verify']['header']
            ckan_upload_api.verify_upload(url, token, file)
            return result

        # File is already in storage
        else:
            result['file_already_exists'] == True
