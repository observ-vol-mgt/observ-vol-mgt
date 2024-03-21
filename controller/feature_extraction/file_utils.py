import requests
import zipfile
import os


def get_file(url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)
    return filename


def unzip_file(filename):
    zip_ref = zipfile.ZipFile(filename, 'r')
    zip_ref.extractall()
    zip_ref.close()


def file_exists(filename):
    return os.path.isfile(filename)
