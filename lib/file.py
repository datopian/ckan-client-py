import os

import hashlib


class FileSystem:
    '''
    This is class for getting file attributes

    Attributes:
        file_path (str): The path to the file
    '''

    def __init__(self, file_path):
        self.file_path = file_path

    def get_name(self):
        return os.path.basename(self.file_path)

    def get_size(self):
        stat_obj = os.stat(self.file_path)
        return stat_obj.st_size

    def get_content(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def get_sha256(self, block_size=50000):
        sha256 = hashlib.sha256()

        with open(self.file_path, 'rb') as file:
            for block in iter(lambda: file.read(block_size), b''):
                sha256.update(block)

        return sha256.hexdigest()


