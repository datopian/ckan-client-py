#from urllib.parse import urljoin
from urlparse import urljoin
import mock

from ckanclient.client import Client
from ckanclient import f11s


config = {
  'auth_token': 'f75160d3-a876-4b43-8a6f-2dc7a693031f',
  'base_url': 'http://127.0.0.1:5000',
  'organization_id': 'test-org',
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


ckan_uploader = Client(config['base_url'],
                config['auth_token'],
                config['organization_id'],
            )

def test_can_instantiate_uploader():
    datahub = Client(config['base_url'],
                config['auth_token'],
                config['organization_id'],
            )
    assert datahub.base_url == config['base_url']


get_jwt_from_ckan_authz_json = {
                    "help": "http://127.0.0.1:5000/api/3/action/help_show?name=authz_authorize",
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
                    'oid': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                    'size': 1691,
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

dataset_resp = {
  'result': {
    'id': 'abc-123-xyz-321',
    'name': 'test-dataset',
    'owner_org': 'test-org'
    }
  }
resource_resp = {
  'result': {
    'id': 'abc-123-xyz-321',
    'size': 1691,
    'hash': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'path': './tests/sample_file/dailyprices.csv'
    }
  }

@mock.patch("ckanclient.client.Client.get_jwt_from_ckan_authz", return_value=get_jwt_from_ckan_authz_json)
@mock.patch("ckanclient.client.Client.request_file_upload_actions", return_value=request_file_upload_actions_json)
@mock.patch("ckanclient.client.Client.upload_to_storage", return_value=True)
@mock.patch("ckanclient.client.Client.verify_upload", return_value=True)
@mock.patch("ckanclient.client.Client._ckan_package_or_resource_api_call", side_effect = [dataset_resp, resource_resp])
def test_push(get_jwt_from_ckan_authz_mock, request_file_upload_actions_mock,
                                          upload_to_storage_mock, verify_upload_mock
                                          ,_ckan_package_or_resource_api_call_mock):

    resource = f11s.load('./tests/sample_file/dailyprices.csv')
    dataset = f11s.Dataset({'name': 'test-dataset'})
    dataset.add_resource(resource)
    result = ckan_uploader.push(dataset)[0]

    assert result['success'] == True
    assert result['size'] == 1691
    assert result['oid'] == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

@mock.patch("ckanclient.client.Client.get_jwt_from_ckan_authz", return_value=get_jwt_from_ckan_authz_json)
@mock.patch("ckanclient.client.Client.request_file_upload_actions", return_value=request_file_upload_actions_json)
@mock.patch("ckanclient.client.Client.upload_to_storage", return_value=True)
@mock.patch("ckanclient.client.Client.verify_upload", return_value=True)
@mock.patch("ckanclient.client.Client._ckan_package_or_resource_api_call", return_value = resource_resp)
@mock.patch("ckanclient.client.Client._get_ckan_dataset", return_value = dataset_resp)
def test_push_resource_with_existing_dataset(get_jwt_from_ckan_authz_mock, request_file_upload_actions_mock,
                                          upload_to_storage_mock, verify_upload_mock,
                                          _ckan_package_or_resource_api_call_mock,
                                          _get_ckan_dataset_mock):

    result = ckan_uploader.push_resource('./tests/sample_file/dailyprices.csv', 'test-dataset')[0]

    assert result['success'] == True
    assert result['size'] == 1691
    assert result['oid'] == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

@mock.patch("ckanclient.client.Client.get_jwt_from_ckan_authz", return_value=get_jwt_from_ckan_authz_json)
@mock.patch("ckanclient.client.Client.request_file_upload_actions", return_value=request_file_upload_actions_json)
@mock.patch("ckanclient.client.Client.upload_to_storage", return_value=True)
@mock.patch("ckanclient.client.Client.verify_upload", return_value=True)
def test_store_blob(get_jwt_from_ckan_authz_mock, request_file_upload_actions_mock,
                                          upload_to_storage_mock, verify_upload_mock):

    result = ckan_uploader.store_blob('./tests/sample_file/dailyprices.csv')

    assert result['success'] == True
    assert result['size'] == 1691
    assert result['oid'] == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

@mock.patch("ckanclient.client.Client._ckan_package_or_resource_api_call", side_effect = dataset_resp)
def test_update_dataset(_ckan_package_or_resource_api_call_mock):

  
  dataset = f11s.Dataset({'name': 'test-dataset', 'id': 'abc-123-xyz-321', 'owner_org': 'test-org'})
 
  result = ckan_uploader.update_dataset(dataset)
  assert result['id']=='abc-123-xyz-321'
  assert result['name'] == 'test-dataset'
  assert result['owner_org'] == 'test-org'