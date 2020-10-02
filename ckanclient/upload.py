from pathlib import Path

import requests


class CkanUploadAPIError(Exception):
    pass


def push_data_to_blob_storage(action, resource):
    """Send a POST request with specific payload to the URL given by the Batch
    API response."""
    response = requests.put(
        action["href"],
        headers=action["header"],
        data=Path(resource["path"]).read_bytes(),
    )

    if response.status_code < 200 or response.status_code >= 300:
        msg = (
            'Uploading the file to storage failed. The API returned a '
            f'status code {response.status_code}:\n{response.text}'
        )
        raise CkanUploadAPIError(msg)

    return True


def verify_upload(action, resource):
    """Makes a request to the verify URL given by the Batch API response."""
    headers = {
        'Accept': 'application/vnd.git-lfs+json',
        'Content-Type': 'application/vnd.git-lfs+json',
    }
    headers.update(action["header"])
    data = {'oid': resource["descriptor"]["hash"], 'size': resource["size"]}
    response = requests.post(action["href"], headers=headers, json=data)

    # If the file is not found, we get a 404 with {message: '…'}
    if response.status_code != 200:
        raise CkanUploadAPIError(response.json()['message'])

    return True
