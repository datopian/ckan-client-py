import os
import hashlib


def load(file_path):
    # Return a descriptor of the file

    file_descriptor = {}

    file_descriptor['name'] = os.path.basename(file_path)

    file_descriptor['path'] = file_path

    stat_obj = os.stat(file_path)
    file_descriptor['size'] = stat_obj.st_size

    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        for block in iter(lambda: file.read(50000), b''):
            sha256.update(block)

        file_descriptor['hash'] = sha256.hexdigest()

    return file_descriptor


class Dataset:
    '''
    This is a class for creating a dataset

    Attributes:
        descriptor (dict): dict object of a dataset description
    '''

    def __init__(self, descriptor={}):
        self.descriptor = descriptor

    def add_resource(self, resource_descriptor):
        self.descriptor['resources'] = []
        self.descriptor['resources'].append(resource_descriptor)
        return resource_descriptor
