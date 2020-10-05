<div align="center">

# CKAN Client: Python SDK

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datopian/ckan3-py-sdk/issues)
[![ckan-client-py actions](https://github.com/datopian/ckan-client-py/workflows/ckan-client-py%20actions/badge.svg)](https://github.com/datopian/ckan-client-py/actions?query=workflow%3A%22ckan-client-py+actions%22)
[![The MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)

CKAN 3 SDK for CKAN instances with CKAN v3 style cloud storage.<br> This SDK will communicate with [`ckanext-authz-service`](https://github.com/datopian/ckanext-authz-service) (using CKAN to provide authorization tokens for other related systems) and [Giftless](https://github.com/datopian/giftless) (a highly customizable and extensible Git LFS server implemented in Python) to upload data to blob storage.

Read more about [it's design](http://tech.datopian.com/blob-storage/#direct-to-cloud-upload).

</div>

## Install

All you need is [Git](https://git-scm.com/), and [Python](https://www.python.org/) 3.6+ with a [PEP 527](https://www.python.org/dev/peps/pep-0517/) compliant tool, such as [Poetry](https://python-poetry.org/).

First, clone this repository:

```console
$ git clone https://github.com/datopian/ckan-client-py.git
```

Then, move to is directory:

```console
$ cd ckan-client-py
```
And install the package and its dependencies, for example, with Poetry:

```console
$ poetry install
```

## Usage

### `ckanclient.Client`

Arguments:

| Name           | Description       |
| -------------- | ----------------- |
| `api_url`      | CKAN API key      |
| `api_key`      | CKAN instance URL |
| `organization` | Organization      |
| `dataset_id`   | Dataset id        |
| `lfs_url`      | Git LFS URL       |


Example:

```python
from ckanclient import Client


client = Client(
    '771a05ad-af90-4a70-beea-cbb050059e14',
    'http://localhost:5000',
    'datopian',
    'dailyprices',
    'http://localhost:9419',
)
```

These settings matches the standard of [`ckanext-blob-storage`](https://github.com/datopian/ckanext-blob-storage) development environment, but you still need to create the user and organization there.

###  `ckanclient.Client.action`

Arguments:

| Name                 | Type       | Default    | Description                                                  |
| -------------------- | ---------- | ---------- | ------------------------------------------------------------ |
| `name`               | `str`      | (required) | The action name, for example, `site_read`, `package_show`…   |
| `payload`            | `dict`     | (required) | The payload being sent to CKAN. If a payload is provided for a GET request, it will be converted to URL parameters and each key will be converted to snake case. |
| `http_get`           | `bool`     | `False`    | Optional, if `True` will make `GET` request, otherwise `POST`. |
| `transform_payload`  | `function` | `None`     | Function to mutate the `payload` before making the request (useful to convert to and from CKAN and Frictionless formats). |
| `transform_response` | `function` | `None`     | function to mutate the response data before returning it (useful to convert to and from CKAN and Frictionless formats). |

This method is used internally by the following methods.

### `ckanclient.Client.create`

Arguments:

| Name                       | Type            | Description                                                  |
| -------------------------- | --------------- | ------------------------------------------------------------ |
| `dataset_name_or_metadata` | `str` or `dict` | It is either a string being a valid dataset name or dictionary with meta-data for the dataset in Frictionless format. |

Example:

```python
dataset = client.create('dailyprices')
```

### `ckanclient.Client.push`

Arguments:

| Name               | Type   | Description                               |
| ------------------ | ------ | ----------------------------------------- |
| `dataset_metadata` | `dict` | Dataset meta-data in Frictionless format. |

Example:

```python
dataset_metadata = {
    'id': '16d6e8d7-a848-48b1-91d0-fd393c1c6c01',
    'name': 'dailyprices',
    'owner_org': '57f97769-a982-4ccd-91f0-1d86dee822e3',
    'title': 'dailyprices',
    'type': 'dataset',
    'contributors': [],
    # …
}
dataset = client.push(dataset_metadata)
```

###  `ckanclient.Client.retrieve`

Arguments:

| Name         | Type  | Description                |
| ------------ | ----- | -------------------------- |
| `name_or_id` | `str` | Id or name of the dataset. |

Example:

```python
dataset = client.retrieve('dailyprices')
```

### `ckanclient.Client.push_blob`

Arguments:

| Name       | Type   | Description              |
| ---------- | ------ | ------------------------ |
| `resource` | `dict` | A Frictionless resource. |


## Tests

To run tests:

```console
$ poetry run pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](License) file for details
