from contextlib import contextmanager
from pathlib import Path

import pytest
from vcr import use_cassette

from ckanclient import Client


API_KEY = 'c15faba1-3792-426a-abb8-9501342ac38b'
API_URL = 'http://localhost:5000'
ORGANIZATION = 'datopian'
DATASET = 'dailyprices'
LFS_URL = 'http://0.0.0.0:9419'


@pytest.fixture
def sample_file():
    path = Path() / 'tests' / 'sample_file' / 'dailyprices.csv'
    return str(path)


@pytest.fixture
def vcr():
    @contextmanager
    def vcr_wrapper(path):
        path = Path(__file__).parent / 'vcr' / path
        with use_cassette(str(path)):
            yield

    return vcr_wrapper


@pytest.fixture
def client():
    return Client(API_URL, API_KEY, ORGANIZATION, DATASET, LFS_URL)


@pytest.fixture
def auth(client):
    return client.auth
