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
from ckan_sdk import client

client_obj = client.Client(endpoint, token_api_key, organization_name, dataset_name)

## Porcelain
client_obj.push('path-to-resource')

# you can also push a set of files
# if directory we search for all *.csv ...
client_obj.push_resources(resources)

## Plumbing
client_obj.store_blob()
client_obj.push_resource_metadata() # resource_update
client_obj.push_dataset_metadata()  # package_update
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
