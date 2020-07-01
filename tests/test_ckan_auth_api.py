import requests
import requests_mock
from urllib.parse import urljoin


AUTH_TOKEN = '22cd879726c64fab712484673f3c034e5ef37552'
SCOPE = 'obj:myorg/dataset-name/*:write'

BODY = {
      'scopes': SCOPE,
    }
HEADERS = {
        'Content-Type': 'application/json;charset=utf-8',
        'Authorization': AUTH_TOKEN,
    }

BASE_URL = 'http://127.0.0.1:5000'
PATH = '/api/3/action/authz_authorize'

@requests_mock.Mocker()
def mock_get_jwt_from_ckan_authz(m, json_resp):
    m.post(urljoin(BASE_URL, PATH), json=json_resp)
    return requests.post(urljoin(BASE_URL, PATH), headers=HEADERS, data=BODY)

def test_ckan_authz():
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

    response = mock_get_jwt_from_ckan_authz(json_resp)
    assert response.status_code == 200
    assert response.json == json_resp
