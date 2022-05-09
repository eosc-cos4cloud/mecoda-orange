from setuptools import setup

# incluir documentación de https://github.com/biolab/orange3-example-addon/blob/master/setup.py

NAME = "Orange3 MECODA Add-on"
VERSION = "1.0.1"

AUTHOR = "Ana Alvarez, ICM-CSIC"
AUTHOR_EMAIL = "ana.alvarez@icm.csic.es"

URL = 'https://github.com/eosc-cos4cloud/mecoda-orange'

DESCRIPTION = "Add-on containing MECODA widgets to analyse data from citizen science observatories"

LICENSE = "BSD"

KEYWORDS = [
    'orange3 add-on',
    ]

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

setup(
    name="mecoda_orange",
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description=DESCRIPTION,
    license=LICENSE,
    packages=["mecoda_orange"],
    package_data={"mecoda_orange": ["icons/*"]},
    classifiers=[
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta"
        ],
    entry_points={"orange.widgets": "MECODA = mecoda_orange"},
    install_requires=[
        "flat_table >= 1.1.1",
        "mecoda-nat >= 0.5.8",
        "pandas >= 1.4.1",
        "Orange3 >= 3.31.1",
        "pyodourcollect >= 1.0.0",
        "ictiopy >= 1.0.0"
        ],
    keywords=KEYWORDS,
    )


