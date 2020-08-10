<div align="center">

# ckan3-py-sdk

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datopian/ckan3-py-sdk/issues)
![ckan3-py-sdk actions](https://github.com/datopian/ckan3-py-sdk/workflows/ckan3-py-sdk%20actions/badge.svg)
[![The MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](http://opensource.org/licenses/MIT)


CKAN 3 SDK for CKAN instances with CKAN v3 style cloud storage.<br> This SDK will communicate with [Ckanext-authz-service](https://github.com/datopian/ckanext-authz-service)(Use CKAN to provide authorization tokens for other related systems
), [giftless service](https://github.com/datopian/giftless)(A highly customizable and extensible Git LFS server implemented in Python) and uploading to Blob storage.

</div>

## Install

First, clone the repo via git:

```bash
$ git clone git@github.com:datopian/ckan3-py-sdk.git
```

Move to directory:

```bash
$ cd ckan3-py-sdk
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
from ckan_sdk import f11s
from ckan_sdk import client

endpoint = 'https://my-ckan.com/'
auth_token = 'xxxx'                   # your CKAN API key
organization_name = 'my-organization' # the default organization on CKAN to add datasets to
client_obj = client.Client(endpoint, auth_token, organization_name)

# loads a resource from a path
resource = f11s.load(resource_file_path)
print(resource)
# resource = {
#     name: ...
#     path: ...
#     hash: ...
#     size: ...
#   }

dataset = f11s.Dataset({'name': dataset_name})
dataset.add_resource(resource)

# Push the dataset and resources to CKAN and resources to cloud cloud
res = client_obj.push(dataset)
print(res)
# res = [{
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'dataset': ...
#     }]


resource_path = 'path/to/file'
# To push a single resource to ckan and cloud
# `append` specifies that dataset already exists
res = client.push_resource(resource_path, dataset='dataset-name', append=True)
print(res)
# res = [{
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'dataset': ...
#     }]


# To push a single resource to cloud only
res = client.store_blob(resource_path)
# res = {
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'verify_url': ...
#     'verify_token': ...
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
