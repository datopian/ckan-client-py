from contextlib import contextmanager
from pathlib import Path

import pytest
from vcr import use_cassette

from ckanclient import CkanClient
from ckanclient.auth import CkanAuthApi


API_KEY = '771a05ad-af90-4a70-beea-cbb050059e14'
API_URL = 'http://localhost:5000'
ORGANIZATION = 'datopian'
DATASET = 'dailyprices'
LFS_URL = 'http://0.0.0.0:9419'


@pytest.fixture
def sample_file():
    path = Path(__file__).parent / 'sample_file' / 'dailyprices.csv'
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
def auth():
    return CkanAuthApi(API_URL, API_KEY, ORGANIZATION, DATASET)


@pytest.fixture
def client():
    return CkanClient(API_URL, API_KEY, ORGANIZATION, DATASET, LFS_URL)
