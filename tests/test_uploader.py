from urllib.parse import urljoin

import mock

from lib.ckan_client import Uploader
from lib.file import FileSystem


config = {
  'auth_token': 'f75160d3-a876-4b43-8a6f-2dc7a693031f',
  'base_url': 'http://127.0.0.1:5000',
  'organization_id': 'test-org',
  'dataset_id': 'xloader_dataset',
}

ckan_authz_config = {
  'body': {
    'scopes': ["obj:{}/{}/*:write".format(config['organization_id'], config['dataset_id'])],
  },
}

access_granter_config = {
  'body': {
    'operation': 'upload',
    'transfers': ['basic'],
    'ref': { 'name': 'refs/heads/contrib' },
    'objects': [
      {
        'oid': '7b28186dca74020a82ed969101ff551f97aed110d8737cea4763ce5be3a38b47',
        'size': 701,
      },
    ],
  },
  'headers': {
    'Accept': 'application/vnd.git-lfs+json',
    "Content-Type": 'application/vnd.git-lfs+json',
    'Authorization':
      'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMi===',
  },
}

cloud_storage_config = {
  'base_url': 'https://myaccount.blob.core.windows.net/mycontainer',
  'path': '/my-blob',
  'body': {},
}

ckan_uploader = Uploader(config['base_url'],
                config['auth_token'],
                config['organization_id'],
                config['dataset_id'],
            )

file = FileSystem('./tests/sample_file/dailyprices.csv')

def test_can_instantiate_uploader():
    datahub = Uploader(config['base_url'],
                config['auth_token'],
                config['organization_id'],
                config['dataset_id'],
            )
    assert datahub.base_url == config['base_url']


get_jwt_from_ckan_authz_json = {
                    "help": "http://localhost:5000/api/3/action/help_show?name=authz_authorize",
                    "success": True,
                    "result": {
                      "requested_scopes": [
                          "obj:myorg/dataset-name/*:write"
                      ],
                      "granted_scopes": [],
                      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiIiLCJ==",
                      "user_id": "admin",
                      "expires_at": "2020-04-22T20:08:41.102934+00:00"
                    }
                }

request_file_upload_actions_json = {
            'transfer': 'basic',
            'objects': [
                {
                    'oid': '8857053d874453bbe8e7613b09874e2d8fc9ddffd2130a579ca918301c31b369',
                    'size': 123,
                    'authenticated': True,
                    'actions': {
                    'upload': {
                        'href': 'https://myaccount.blob.core.windows.net/mycontainer/my-blob',
                        'header': access_granter_config['headers'],
                        'expires_in': 86400,
                    },
                    'verify': {
                        'href': 'https://some-verify-callback.com',
                        'header': {
                        'Authorization': 'Bearer TOKEN',
                        },
                        'expires_in': 86400,
                    },
                    },
                  },
              ],
          }

@mock.patch("lib.util.ckan_auth_api.get_jwt_from_ckan_authz", return_value=get_jwt_from_ckan_authz_json)
@mock.patch("lib.util.ckan_auth_api.request_file_upload_actions", return_value=request_file_upload_actions_json)
@mock.patch("lib.util.ckan_upload_api.upload_to_storage", return_value=True)
@mock.patch("lib.util.ckan_upload_api.verify_upload", return_value=True)
def test_push_works_with_packaged_dataset(get_jwt_from_ckan_authz_mock, request_file_upload_actions_mock,
                                          upload_to_storage_mock, verify_upload_mock):
    import pdb; pdb.set_trace()

    token = ckan_uploader.ckan_authz()['result']['token']
    ckan_uploader.push(file, token)

    assert token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiIiLCJ=='

def test_dataset_not_altered():
    size = file.get_size()
    sha256 = file.get_sha256()

    assert size == 1691
    assert sha256 == 'eb0a6b68972615a24502f50e06d6b33fc5f60f3e1d05c5c65c54c2f3248e3c9b'
