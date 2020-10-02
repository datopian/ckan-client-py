import pytest

from ckanclient.text import camel_to_snake


@pytest.mark.parametrize(
    'value,expected',
    (
        ('camel2_camel2_case', 'camel2_camel2_case'),
        ('getHTTPResponseCode', 'get_http_response_code'),
        ('HTTPResponseCodeXYZ', 'http_response_code_xyz'),
    ),
)
def test_camel_to_snake(value, expected):
    assert camel_to_snake(value) == expected
