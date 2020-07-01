from urllib.parse import urljoin

import requests
import requests_mock
from lib.index import Uploader
from lib.file_api import FileSystem


config = {
  'auth_token': 'be270cae-1c77-4853-b8c1-30b6cf5e9878',
  'api': 'http://127.0.0.1',
  'organization_id': 'myorg',
  'dataset_id': 'dataset-name',
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
  'api': 'https://myaccount.blob.core.windows.net/mycontainer',
  'path': '/my-blob',
  'body': {},
}

@requests_mock.Mocker()
def mock_ckan_authz(mock_request):
    json_resp = {
        "help": "http://localhost:5000/api/3/action/help_show?name=authz_authorize",
        "success": True,
        "result": {
        "requested_scopes": [
            "obj:myorg/dataset-name/*:write"
        ],
        "granted_scopes": [],
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZXMiOiIiLCJ== ",
        "user_id": "admin",
        "expires_at": "2020-04-22T20:08:41.102934+00:00"
        }
    }

    mock_request.post(urljoin(config['api'], '/api/3/action/authz_authorize'), json=json_resp)

    return requests.post(urljoin(config['api'], '/api/3/action/authz_authorize'),
                    data=ckan_authz_config['body'])

@requests_mock.Moocker()
def mock_cloud_storage_access_granter_service(mock_request):
    json_resp = {
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
    mock_request.post(urljoin(config['api'], '/api/3/action/authz_authorize'), json=json_resp)

    return requests.post(urljoin(config['api'], '/api/3/action/authz_authorize'),
                    data=access_granter_config['body'])

@requests_mock.Mocker()
def mock_cloud_storage(mock_request):
    json_resp = { 'success': True }

    mock_request.put(urljoin(cloud_storage_config['api'], cloud_storage_config['path']), json=json_resp)

    return requests.put(urljoin(cloud_storage_config['api'], cloud_storage_config['path']),
                    data=cloud_storage_config['body'], headers=access_granter_config['headers'])

@requests_mock.Mocker()
def mock_verify_file_upload(mock_request):
    json_resp = {
            'message': "Verify Uploaded Successfully",
            'success': True,
        }

    mock_request.post('https://some-verify-callback.com/', json=json_resp)

    return requests.post('https://some-verify-callback.com/')


ckan_uploader = Uploader(config['auth_token'],
                config['organization_id'],
                config['dataset_id'],
                config['api']
            )

file = FileSystem('./test/fixtures/sample.csv')

def test_can_instantiate_uploader():
    datahub = Uploader(config['auth_token'],
                config['organization_id'],
                config['dataset_id'],
                config['api']
            )
    assert datahub.api == config['api']

def test_push_works_with_packaged_dataset():
    token = ckan_uploader.ckan_authz()['result']['token']
    ckan_uploader.push(file, token)

    assert mock_ckan_authz().status_code == 200
    assert mock_cloud_storage_access_granter_service() == 200
    assert mock_cloud_storage().status_code == 201
    assert mock_verify_file_upload().status_code == 200

def test_dataset_not_altered():
    size = file.size()
    sha256 = file.sha256()

    assert size == 701
    assert sha256 == '7b28186dca74020a82ed969101ff551f97aed110d8737cea4763ce5be3a38b47'
