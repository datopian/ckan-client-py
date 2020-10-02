import logging

import requests
from frictionless_ckan_mapper import ckan_to_frictionless, frictionless_to_ckan

from ckanclient.auth import CkanAuthApi
from ckanclient.text import camel_to_snake
from ckanclient.upload import push_data_to_blob_storage, verify_upload


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
log = logging.getLogger(__name__)


class CkanClientError(Exception):
    pass


class CkanClient:
    def __init__(self, api_url, api_key, organization, dataset_id, lfs_url):
        self.api_url = api_url
        self.api_key = api_key
        self.organization = organization
        self.dataset_id = dataset_id
        self.lfs_url = lfs_url
        self.auth = CkanAuthApi(api_url, api_key, organization, dataset_id)

    def action(
        self,
        name,
        payload,
        http_get=False,
        transform_payload=None,
        transform_response=None,
    ):
        """Gives you direct access to the CKAN Action API
        (https://docs.ckan.org/en/2.8/api/).

        Attributes:
            name (str): The action name, e.g. site_read, package_show…
            payload (dict): The payload being sent to CKAN. If a payload is
                provided for a GET request, it will be converted to URL
                parameters and each key will be converted to snake case.
            http_get (bool): Optional, if `True` will make `GET` request,
                otherwise `POST`.
            transform_payload (func): Function to mutate the `payload` before
                making the request (useful to convert to and from CKAN and
                Frictionless formats).
            transform_response (func): Function to mutate the response data
                before returning it (useful to convert to and from CKAN and
                Frictionless formats).

        Returns:
            dict: the API response converted from JSON to a Python dictionary.
        """
        url = f'{self.api_url}/api/3/action/{name}'
        headers = {
            'Content-Type': 'application/json;charset=utf-8',
            'Authorization': self.api_key,
        }
        if transform_payload:
            payload = transform_payload(payload)

        if http_get:
            params = {camel_to_snake(k): v for k, v in payload.items()}
            response = requests.get(url, headers=headers, params=params)
        else:
            response = requests.post(url, headers=headers, data=payload)

        if response.status_code < 200 or response.status_code >= 300:
            msg = (
                'CKAN Action API returned HTTP Status Code '
                f'{response.status_code}:\n{response.text}'
            )
            raise CkanClientError(msg)

        data = response.json()
        return transform_response(data) if transform_response else data

    def create(self, dataset_name_or_metadata):
        """Creates a new dataset.

        Attributes:
            dataset_name_or_metadata (str or dict): It is either a string
                being a valid dataset name or metadata for the dataset in
                Frictionless format.

        Returns:
            dict: the newly created dataset.
        """
        metadata = dataset_name_or_metadata
        if isinstance(metadata, str):
            metadata = {
                'name': dataset_name_or_metadata,
                'owner_org': self.organization,
            }

        return self.action(
            'package_create',
            metadata,
            transform_payload=ckan_to_frictionless.dataset,
            transform_response=frictionless_to_ckan.resource,
        )

    def push(self, dataset_metadata):
        """Updates the dataset.

        Attributes:
            dataset_metadata (dict): the metadata in Frictionless format.

        Returns:
            dict: the updated dataset.
        """
        return self.action(
            'package_update',
            dataset_metadata,
            transform_payload=ckan_to_frictionless.dataset,
            transform_response=frictionless_to_ckan.resource,
        )

    def retrieve(self, name_or_id):
        """Retrieves the dataset.

        Attributes:
            name_or_id (str): Id or name of the dataset.

        Returns:
            dict: a Frictionless dataset.
        """
        return self.action(
            'package_show',
            {'id': name_or_id},
            http_get=True,
            transform_response=ckan_to_frictionless.resource,
        )

    def push_blob(self, resource):  # TODO async version with on_progress attr
        """Gets the result of push blob method.

        Attributes:
            resource (dict): A Fricionless resource.

        Returns:
            dict: the push blob result has the keys `oid` (str), `size` (int)
                of the file, `name` (str) of the resource, `success` (bool) of
                the request, and `file_exists` (bool) indicating whether the
                resource existed or not.
        """
        lfs = self.auth.request_file_upload_actions(resource)
        obj, *_ = lfs['objects']
        result = {
            'oid': obj['oid'],
            'size': obj['size'],
            'name': resource['descriptor']['name'],
            'success': True,
            'fileExists': True,
        }

        if not obj["actions"]:  # File is already in storage
            return result

        result["file_exists"] = False
        push_data_to_blob_storage(obj["actions"]["upload"], resource)
        verify_upload(obj["actions"]["verify"], resource)
