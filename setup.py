""" improved_permissions setup configs """
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-improved-permissions',
    version='0.1.2',
    packages=[
        'improved_permissions',
        'improved_permissions.migrations',
        'improved_permissions.templatetags',
    ],
    include_package_data=True,
    license='MIT License',
    description='A Django app to handle all kinds of permissions and roles.',
    long_description=README,
    url='https://github.com/s-sys/django-improved-permissions',
    author='S-SYS Sistemas e Soluções Tecnológicas',
    author_email='contato@ssys.com.br',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ],
)
