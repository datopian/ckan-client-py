<div align="center">

# Ckan3-py-sdk

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datopian/ckan3-py-sdk/issues)
![Python package](https://github.com/datopian/ckan3-py-sdk/workflows/Python%20package/badge.svg)
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
```bash
from ckan_sdk import f11s
from ckan_sdk import client

client_obj = client.Client(endpoint, auth_token, organization_name)

# loads a resource from a path
resource = f11s.load(resource_file_path)
# resource = {
#     name: ...
#     path: ...
#     hash: ...
#     size: ...
#   }

dataset = f11s.Dataset({'name': dataset_name})
dataset.add_resorce(resource)

# Push the dataset and resources to CKAN and resources to cloud cloud
res = client_obj.push(dataset.descriptor)
# res = [{
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'dataset': ...
#     }]

# To push a single resource to ckan and cloud
# `append` specifies that dataset already exists
res = client.push_resource(resource, dataset='dataset-name', append=True)
# res = [{
#     'oid': ...
#     'size': ...
#     'success': ...
#     'file_already_exists': ...
#     'dataset': ...
#     }]
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
