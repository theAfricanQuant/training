"""Setup script"""

import tarfile
import zipfile
import shutil
import argparse
import os

from setuptools import setup, find_packages
from setuptools.command.sdist import sdist
from subprocess import call

PULL_OBJECT_DETECTION = """
    svn export -r 8436 https://github.com/tensorflow/models/trunk/research/object_detection src/object_detection &&
    svn export -r 8436 https://github.com/tensorflow/models/trunk/research/slim src/object_detection/slim &&
    protoc src/object_detection/protos/*.proto --python_out=.
"""

PULL_CLASSIFICATION = """
    svn export -r 308 https://github.com/tensorflow/hub/trunk/examples/image_retraining src/classification
    echo > src/classification/__init__.py
"""

OUTPUT_FILE = 'training.zip'


parser = argparse.ArgumentParser()
parser.add_argument('type')
args = parser.parse_args()


class InstallCommand(sdist):
    def initialize_options(self):
        sdist.initialize_options(self)
        self.custom_option = None

    def finalize_options(self):
        sdist.finalize_options(self)

    def run(self):
        sdist.run(self)


def move_zip(zip_file, name):
    with tarfile.open(f'dist/{name}-0.1.tar.gz') as tar:
        for member in tar.getmembers():
            if (
                member.name.startswith(f'{name}-0.1/{name}/')
                and member.isfile()
            ):
                print(f'in: {member.name}')
                f = tar.extractfile(member)
                rel_path = os.path.relpath(member.name, f'{name}-0.1')
                zip_file.writestr(rel_path, f.read())


setup(
    name='src',
    version='0.1',
    include_package_data=True,
    packages=[p for p in find_packages() if p.startswith('src')],
    description='tf-training',
    cmdclass={
        args.type: InstallCommand,
    }
)
shutil.rmtree('src.egg-info')


if args.type == 'all':
    call(PULL_CLASSIFICATION, shell=True)
    call(PULL_OBJECT_DETECTION, shell=True)

if args.type == 'object_detection':
    call(PULL_OBJECT_DETECTION, shell=True)
  
if args.type == 'classification':
    call(PULL_CLASSIFICATION, shell=True)


with zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED) as tf_model:
    move_zip(tf_model, 'src')


shutil.rmtree('dist')