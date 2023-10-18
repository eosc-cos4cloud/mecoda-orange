# Mecoda-Orange
Orange Data Mining Widgets to analyse data from science citizen observatories.
See [documentation](https://github.com/eosc-cos4cloud/mecoda-orange).

[MECODA (ModulE for Citizen Observatory Data Analysis)](https://cos4cloud-eosc.eu/services/mecoda-data-analysis-package/) is a repository to facilitate analyzing and viewing all sorts of citizen science data. It allows users to make their own exploratory visual data analysis without the help of specialized analysts. It also enables observers to create their own reproducible visual dataflows and share and reuse them. 	

MECODA is part of [Cos4Cloud](https://cos4cloud-eosc.eu/), a European Horizon 2020 project to boost citizen science technologies.

# Features

* **Minka**: collect observations from Minka API, using [mecoda-minka](https://github.com/eosc-cos4cloud/mecoda-minka) library.
* **OdourCollect**: collect observations from OdourCollect API, using [pyodcollect](https://pypi.org/project/pyodcollect/) library.
* **canAIRio**: composed for two widgets, one for [CanAIRio Fixed Stations data](https://canair.io/docs/fixed_stations_api_en.html) and other for [CanAIRio Mobile Stations data](https://canair.io/docs/mobile_api_en.html).
* **Ictio**: process observations from [ictio.org](https://ictio.org) zip file, using [IctioPy](https://github.com/ScienceForChange/IctioPy) library.
* **Natusfera**: collect observations from Natusfera API, using [mecoda-nat](https://github.com/eosc-cos4cloud/mecoda-nat) library.
* **Smart Citizen**: collect observations from the SmartCitizen API, using two widgets, one for collecting information about the kits in the [smartcitizen platform](https://smartcitizen.me/kits) and another one for the actual timeseries data. For making use of the timeseries data, it is necessary to add the orange `timeseries` add-on.
