from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='blueflood-es-reindex',
    version='0.0.1',
    description='Codebase to re-index blueflood Elastic search.',
    long_description=readme,
    author='Chandra Addala',
    author_email='chanddra.addala@rackspace.com',
    url='https://github.com/ChandraAddala/blueflood-es-reindex',
    packages=find_packages(exclude=('tests', 'docs')),

    install_requires=[
        'requests',
        'elasticsearch>=1.0.0,<2.0.0'
    ],

    tests_require=[
        'pytest'
    ]
)
