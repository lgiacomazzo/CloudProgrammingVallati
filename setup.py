# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "swagger_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["connexion"]

setup(
    name=NAME,
    version=VERSION,
    description="My REST API",
    author_email="",
    url="",
    keywords=["Swagger", "My REST API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['swagger/swagger.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['swagger_server=swagger_server.__main__:main']},
    long_description="""\
    This is a server which allows to schedule on an Openstack instance when to schedule VMs (for example during peak periods), while also specifying the flavor needed and the image from which the VMs are instanced, and the number of VMs to create in said period.
    """
)

