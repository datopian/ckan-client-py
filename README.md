<div align="center">

# Ckan3-py-sdk

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/datopian/ckan3-py-sdk/issues)
[![The MIT License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](http://opensource.org/licenses/MIT)


Ckan3-py-sdk is a Python SDK for CKAN with the next generation versioning and file storage.<br> This SDK will communicate with [Ckanext-authz-service](https://github.com/datopian/ckanext-authz-service)(Use CKAN to provide authorization tokens for other related systems
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
Deploy the package:

```bash
$ python deploy setup.py
```


## Developers
```bash
from lib import ckan_client

client = ckan_client.Uploader(endpoint, token_api_key)

## Porcelain
# TODO: dataset_name inferred from file?
client.push(dataset_name, 'path-to-resource', **metadata)

# you can also push a set of files
# if directory we search for all *.csv ...
client.push_resources(dataset_name, resources, **metadata)

## Plumbing
client.store_blob()
client.push_resource_metadata() # resource_update
client.push_dataset_metadata()  # package_update
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
