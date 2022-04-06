from setuptools import setup, find_packages

setup(
    name = "demloader",
    version = "0.1.1",
    author = "Ben Gaffinet",
    author_email = "ben@gaffinet.lu",
    packages = find_packages(include=['demloader'], exclude=['tests', 'notebooks']),
    include_package_data = True,
    test_suite = 'tests',
    install_requires = [
        'gdal',
        'rasterio',
        'boto3',
        'botocore',
        'pyproj',
    ],
    dependency_links = [],
    description = "Single purpose downloader for global Copernicus DEM data.",
    license = 'GPLv3',
    keywords = "dem gis sentinel copernicus download",
    url = "https://github.com/gaffinetB/demloader",
    classifiers = ['Development Status :: 2 - Pre-Alpha',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence',
                   'Topic :: Scientific/Engineering :: GIS',
                   'Intended Audience :: Science/Research',
                   'Programming Language :: Python :: 3.6']
)