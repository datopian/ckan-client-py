import pytest


def test_create(vcr, client):
    with vcr('test_create.yaml'):
        dataset = client.create('dailyprices')
    assert dataset['success']


def test_push(vcr, client):
    dataset_metadata = {
        'creator_user_id': '91f4d037-f220-4bd3-a86d-c24870753b0e',
        'groups': [],
        'id': '16d6e8d7-a848-48b1-91d0-fd393c1c6c01',
        'metadata_created': '2020-10-02T15:35:43.064103',
        'metadata_modified': '2020-10-02T15:35:43.064107',
        'name': 'dailyprices',
        'owner_org': '57f97769-a982-4ccd-91f0-1d86dee822e3',
        'private': False,
        'relationships_as_object': [],
        'relationships_as_subject': [],
        'resources': [],
        'revision_id': '4ee38e73-2f25-4ece-b5da-c7c3370141fb',
        'title': 'dailyprices',
        'type': 'dataset',
        'contributors': [],
    }
    with vcr('test_push.yaml'):
        dataset = client.push(dataset_metadata)
    assert dataset['success']


def test_retrieve(vcr, client):
    with vcr('test_retrieve.yaml'):
        dataset = client.retrieve('dailyprices')
    assert dataset['success']


@pytest.mark.skip('TODO')  # TODO needs a working resource
def test_push_blob(vcr, sample_file, client):
    with vcr('test_push_blob.yaml'):
        pass
