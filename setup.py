from setuptools import setup

setup(
    name='hystore',
    version='0.2.4.dev5',
    description='High-volume key-value store and analytics, based on hdf5',
    url='https://github.com/kcl-bmeis/zoe-data-store',
    author='Ben Murray',
    author_email='benjamin.murray@kcl.ac.uk',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    packages=['hystore', 'hystore.contrib', 'hystore.core', 'hystore.covidspecific', 'hystore.processing'],
    install_requires=[
        'numpy',
        'numba',
        'pandas',
        'h5py'
    ]
)