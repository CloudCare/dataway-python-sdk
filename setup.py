from setuptools import setup, find_packages

setup(
    name='dwadapter',
    version='0.2.0',
    packages=find_packages(),
    author='huangbo',
    url='www.jiagouyun.com',
    author_email='huangbo@jiagouyun.com',
    install_requires = ["pynsq","requests"]
)