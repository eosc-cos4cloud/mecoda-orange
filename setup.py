from setuptools import setup, find_packages
import os


# incluir documentación de https://github.com/biolab/orange3-example-addon/blob/master/setup.py

NAME = "Orange3-MECODA"
DOCUMENTATION_NAME = 'Orange MECODA'

VERSION = "1.8.1"

AUTHOR = "Ana Alvarez, ICM-CSIC"
AUTHOR_EMAIL = "ana.alvarez@icm.csic.es"

URL = 'https://github.com/eosc-cos4cloud/mecoda-orange'

DESCRIPTION = "Add-on containing MECODA widgets to analyse data from citizen science observatories"
LONG_DESCRIPTION = open(os.path.join(
    os.path.dirname(__file__), 'README_pypi.md')).read()
LICENSE = "BSD"

KEYWORDS = [
    'orange3 add-on',
    'orange',
    'data mining',
]
#PACKAGES = find_packages(include=("mecoda_orange*",))
setup(
    name="Mecoda Orange",
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    license=LICENSE,
    packages=["mecoda_orange"],
    # packages=PACKAGES,
    package_data={
        "mecoda_orange": ["icons/*"],
    },
    classifiers=[
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        'Environment :: X11 Applications :: Qt',
        'Environment :: Console',
        'Environment :: Plugins',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta",
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Operating System :: OS Independent',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
    ],
    entry_points={
        "orange.widgets": "MECODA = mecoda_orange",
        "orange.addons": "MECODA = mecoda_orange"
    },
    install_requires=[
        "mecoda-nat >= 0.5.8",
        "pandas >= 1.5.2",
        "Orange3 >= 3.31.1",
        "pyodourcollect >= 1.0.0",
        "ictiopy >= 1.0.0",
        "mecoda-minka >= 1.0.0",
        "smartcitizen-connector >= 0.1.2",
        "pytest"
    ],
    keywords=KEYWORDS,
    include_package_data=True,
    zip_safe=False,
)
