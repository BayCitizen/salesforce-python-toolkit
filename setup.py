from setuptools import setup

setup(
    name='salesforce-python-toolkit',
    version='0.1.3',
    description='A fork of http://code.google.com/p/salesforce-python-toolkit/',
    url='http://github.com/BayCitizen/salesforce-python-toolkit',
    packages=[
        'sforce',
    ],

    install_requires=[
        'suds',
    ],
)
