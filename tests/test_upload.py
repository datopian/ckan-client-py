import pytest

from ckanclient.upload import (
    CkanUploadAPIError,
    push_data_to_blob_storage,
    verify_upload,
)


@pytest.mark.skip('TODO')  # TODO needs a working resource
def test_push_data_to_blob_storage(vcr):
    with vcr('test_push_data_to_blob_storage.yaml'):
        pass


def test_failed_push_data_to_blob_storage(mocker, sample_file):
    response = mocker.Mock()
    response.status_code = 500
    mocker.patch('ckanclient.upload.requests.put', return_value=response)
    action = {'href': 'http://ckan', 'header': {}}
    resource = {
        'path': sample_file,
        'stats': {'hash': '2a', 'bytes': 42},
    }
    with pytest.raises(CkanUploadAPIError):
        push_data_to_blob_storage(action, resource)


@pytest.mark.skip('TODO')  # TODO needs a working resource
def test_verify_upload(vcr):
    with vcr('test_verify_upload.yaml'):
        pass


def test_failed_verify_upload(mocker):
    response = mocker.Mock()
    response.status_code = 500
    response.json.return_value = {'message': 42}
    mocker.patch('ckanclient.upload.requests.post', return_value=response)
    action = {'href': 'http://ckan', 'header': {}}
    resource = {'stats': {'hash': '2a', 'bytes': 42}}
    with pytest.raises(CkanUploadAPIError):
        verify_upload(action, resource)
