import logging
import json

import requests

log = logging.getLogger(__name__)


def upload_to_storage(url, token, file_content, on_progress):
    # Send a POST request with specific payload to the URL given by the Batch API response

    body = file_content
    headers ={
        'Authorization': token,
    }

    if on_progress:
        headers['on_upload_progress'] = on_progress

    response = requests.put(url, body, headers)
    if response.status_code != 201:
        log.exception("Uploading the file to storage failed response: {}".format(response.status_code))
        return

    return True

def verify_upload(url, token, file):
    # Get request to the verify URL given by the Batch API response

    body = json.dumps({
            'oid': file.get_sha256(),
            'size': file.get_size(),
        })
    headers = {
        'Accept': 'application/vnd.git-lfs+json',
        'Content-Type': 'application/vnd.git-lfs+json',
        'Authorization': token,
    }

    response = requests.post(url, body, headers)
    if response.status_code != 200:
        log.exception("Failed to verify upload reponse: {}".format(response.status_code))
        return

    return True
