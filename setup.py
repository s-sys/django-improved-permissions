""" improved_permissions setup configs """
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-improved-permissions',
    version='0.0.12',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A Django app to handle all kinds of permissions and roles.',
    long_description=README,
    # download_url = 'https://github.com/gabrielbiasi/django-improved-permissions/archive/0.0.3.zip',
    # url='https://github.com/gabrielbiasi/django-improved-permissions/tree/0.0.3',
    author='Gabriel de Biasi',
    author_email='biasi131@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
