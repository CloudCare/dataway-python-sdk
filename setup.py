from setuptools import setup, find_packages

# import setuptools
# from distutils.core import setup

setup(
    name='dwadapter',
    version='0.0.1',
    packages=find_packages(),
    author='huangbo',
    url='www.jiagouyun.com',
    author_email='huangbo@jiagouyun.com',
    install_requires = ["pynsq","requests"]
)