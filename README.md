<div align="center">

# ckan-client-py

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datopian/ckan3-py-sdk/issues)
[![ckan-client-py actions](https://github.com/datopian/ckan-client-py/workflows/ckan-client-py%20actions/badge.svg)](https://github.com/datopian/ckan-client-py/actions?query=workflow%3A%22ckan-client-py+actions%22)
[![The MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](http://opensource.org/licenses/MIT)


CKAN 3 SDK for CKAN instances with CKAN v3 style cloud storage.<br> This SDK will communicate with [Ckanext-authz-service](https://github.com/datopian/ckanext-authz-service)(Use CKAN to provide authorization tokens for other related systems
), [giftless service](https://github.com/datopian/giftless)(A highly customizable and extensible Git LFS server implemented in Python) and uploading to Blob storage.

</div>

## Install

First, clone the repo via git:

```bash
$ git clone https://github.com/datopian/ckan-client-py.git
```

Move to directory:

```bash
$ cd ckan-client-py
```
Install the package:

```bash
$ python setup.py install
```
Install requirements.txt:

```bash
$ pip install requirements.txt
```

## Developers

```python
from ckanclient import f11s
from ckanclient.client import Client

endpoint = 'https://my-ckan.com/'
auth_token = 'xxxx'                   # your CKAN API key
organization_name = 'my-organization' # the default organization on CKAN to add datasets to
client = Client(endpoint, auth_token, organization_name)

# loads a resource from a path
resource = f11s.load(resource_file_path)
print(resource)
# resource = {
#     name: ...
#     path: ...
#     hash: ...
#     size: ...
#   }

# Create dataset object with dataset name
dataset = f11s.Dataset({'name': 'sample-dataset'})

# Add resource in dataset object
dataset.add_resource(resource)

# Push the dataset and resources to CKAN and resources to cloud
response = client.push(dataset)
print(response)
# response = [{
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'dataset': ...
#     }]


resource_path = 'path/to/file'
# To push a single resource to ckan and cloud
# `append` specifies that dataset already exists
response = client.push_resource(resource_path, dataset='dataset-name', append=True)
print(response)
# response = [{
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'dataset': ...
#     }]


# To push a single resource to cloud only
response = client.store_blob(resource_path)
print(response)
# response = {
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'verify_url': ...
#     'verify_token': ...
#     }


# Create dataset object with metadata
dataset = f11s.Dataset({'name': 'sample-dataset', 'title': 'sample-dataset',
                        'owner_org': 'my-organization', 'maintainer': 'datopian',
                        'maintainer_email': 'maintainer@datopian.com', 'author': 'datopian,
                        'notes': 'This is sample dataset'})

# Push the dataset and resources with metadata to CKAN and resources to cloud
response = client.push(dataset)
print(response)
# response = {
#     'id': ...
#     'name': ...
#     'title': ...
#     'owner_org': ...
#     'author': ...
#     'private': ...
#     }

# To update dataset with metadata in CKAN
dataset = client.update_dataset(dataset)
print(dataset)
# dataset = {
#     'id': ...
#     'name': ...
#     'title': ...
#     'owner_org': ...
#     'author': ...
#     'private': ...
#     }
```

## Design

- http://tech.datopian.com/blob-storage/#direct-to-cloud-upload

## Tests

To run tests:

```bash
pytest tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](License) file for details
