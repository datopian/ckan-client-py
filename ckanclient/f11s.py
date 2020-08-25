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

    def add_metadata(self, name, owner_org, title = None, maintainer = None,
                    maintainer_email = None, publisher = None, author = None, license_id = None,
                    notes = None, investment_ids = None, geographic_level = None,
                    information_classification = None):
        self.descriptor['name'] = name
        self.descriptor['title'] = title
        self.descriptor['owner_org'] = owner_org
        self.descriptor['maintainer'] = maintainer
        self.descriptor['maintainer_email'] = maintainer_email
        self.descriptor['publisher'] = publisher
        self.descriptor['author'] = author
        self.descriptor['license_id'] = license_id
        self.descriptor['notes'] = notes
        self.descriptor['investment_ids'] = investment_ids
        self.descriptor['geographic_level'] = geographic_level
        self.descriptor['information_classification'] = information_classification
