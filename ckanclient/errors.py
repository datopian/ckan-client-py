from requests import Response
from simplejson.errors import JSONDecodeError


class ResponseError(Exception):
    def __init__(self, response, *args, **kwargs):
        if not isinstance(response, Response):
            super(ResponseError, self).__init__(response, *args, **kwargs)
            return

        msg = (
            f'CKAN Action API returned HTTP {response.status_code} '
            f'for {response.request.method.upper()} {response.request.url}'
        )

        try:
            msg += f':\n{response.json()}'
        except JSONDecodeError:
            pass

        super(ResponseError, self).__init__(msg, *args, **kwargs)
