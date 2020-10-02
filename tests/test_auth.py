import pytest

from ckanclient.auth import CkanAuthApiError, json_from_post


def test_json_from_post(mocker):
    response = mocker.Mock()
    response.status_code = 200
    response.json.return_value = {'ok': 42}
    mocker.patch('ckanclient.auth.requests.post', return_value=response)
    assert json_from_post('http://ckan', json={'scopes': []}) == {'ok': 42}


def test_failed_json_from_post(mocker):
    response = mocker.Mock()
    response.status_code = 500
    response.json.return_value = {'error': 42}
    mocker.patch('ckanclient.auth.requests.post', return_value=response)
    with pytest.raises(CkanAuthApiError):
        json_from_post('http://clan', json={'scopes': []})


def test_get_jwt_token(auth, vcr):
    scope = ['obj:datopian/dailyprices/*:write']
    with vcr('test_get_jwt_token.yaml'):
        response = auth.get_jwt_from_ckan_authz(scope)
    assert isinstance(response['result']['token'], str)


def test_do_blob_authz(auth, vcr):
    with vcr('test_do_blob_authz.yaml'):
        assert isinstance(auth.do_blob_authz(), str)


def test_failed_do_blob_authz(auth, mocker):
    mocker.patch('ckanclient.auth.json_from_post', return_value={'error': 42})
    with pytest.raises(CkanAuthApiError):
        auth.do_blob_authz()


@pytest.mark.skip('TODO')  # TODO needs a working resource
def test_request_file_upload_actions(auth, vcr):
    with vcr('test_request_file_upload_actions.yaml'):
        pass
