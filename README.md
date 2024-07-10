# <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/share.png" alt="mecoda-logo" width="100"/> Mecoda-Orange 

This repository includes different Orange Data Mining widgets to access data from [Minka](https://minka-sdg.org/), [Odour Collect](https://odourcollect.eu/), [canAIRio](https://canair.io/), [Aire Ciudadano](https://aireciudadano.com/), [INaturalist](https://www.inaturalist.org/) or [Smart Citizen](https://smartcitizen.me).

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/cos4cloud.png" alt="cos4cloud-logo" width="75"/> MECODA is part of [Cos4Cloud](https://cos4cloud-eosc.eu/), a European Horizon 2020 project to boost citizen science technologies.

To use MECODA package you need to install Orange Data Mining platform through https://orangedatamining.com/download

Once Orange is installed, inside the Options menu, it's possible to get the package using the "Add-ons" category, clicking on "Add more" and searching by name "mecoda-orange". The last version of the package will be installed on the Orange platform.

You can find also a ["Installation Guide"](https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/docs/english/installation_guide.md), ["Orange Example of Use"](https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/docs/english/orange_example_of_use.md) and ["MECODA example of use"]("https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/docs/english/datathon_nov2023_eng.md").

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka-logo.png" alt="minka-logo" width="75"/> Minka widget 

This widget collects observations from Minka API and allows filtering them by:

| Argument | Description | Example |
| --------- | ----------- | ------- |
| `Taxon` | One of the main taxonomies | `taxon=Aves` |
| `Taxon ID` | Number of a taxon | `taxon_id=1110` |
| `Project ID` | Number of a project | `project_id=16` |
| `Place ID` | Name of a place | `place_id=247` |
| `User name` | Name of user who has uploaded the observations | `user="zolople"` |
| `Observation date` | Filters for observations date | `starts_on=2024-06-01` |
| `Creation date` | Filters for upload date | `since=2024-06-01` |
| `Research grade only` | Checkbox to select just research grade observations  | `research_grade=True` |
| `Max. number of results` | Queries of less than 10,000 observations are recommended due to time requeriments | `num_max=800` |

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka-widget.png" alt="minka-widget" width="350"/><img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/map_filter_workflow2.png" alt="minka-widget2" width="350"/>

The Minka widget integrates the Python library `mecoda-minka` into a visual interface. 
You can make any query and download two outputs, a dataframe with one observation per row and a dataframe with one photo per row. 
A single observation can have more than a photo. 

The observations output gets a Table with the following fields:
* **id**: observation id
* **captive**: True or False
* **created_at**: date field.
* **updated_at**: date field.
* **observed_on**: date field.
* **description**: open text field.
* **latitude / longitude**: geo location fields.
* **quality_grade**: needs_id / research.
* **user_login**: user login name.
* **num_identification_agreements / num_identification_disagreements**
* **identifications_count**: number of identifications for an observation.
* **iconic_taxon**: one of the big taxonomic groups available in Minka.
* **taxon_id**: species taxon id.
* **taxon_name**: species name of observation.
* **taxon fields**:
  * kingdom
  * class
  * order
  * superfamily
  * family
  * genus

The `observations` table allows to make statistical analysis. The photos table allows image analysis.

The widget is complemented with other widgets that can take input from it or directly from Minka API:

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/camera-minka.png" alt="get-images" width="50"/> get_images

This widget takes a `Table` with observations (and a column with IDs from Minka) and gets the photos from all of them. Works with data from Minka Widget. 

The output is a Table with an image type feature that can be accessed using `Image Viewer`.

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/arrow-down-wide-short-solid-minka.png" alt="taxon-filter" width="50"/> Minka Taxon Filter

This widget allows the user to filter Minka observations by different taxonomic levels (from kingdom to species). The levels shown are just the ones with registered observations.

The widget looks like this:
### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka_taxon_filter_2.png" alt="taxon-filter-widget" width="350"/> 

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/leaf-solid-minka.png" alt="taxon-filter-by-words" width="50"/> Minka Taxon Search

This widget allows the user to filter Minka observations by scientific or common name.

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka_taxon_search_widget.png" alt="taxon-search-widget" width="350"/> 

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/fish-minka.png" alt="fish-minka.png" width="50"/> Marine and Terrestrial Filter

The widget splits the Table of observations into two dataframes: one for marine species and the other for terrestrial ones. Just gets observations with a research degree.

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/marine_filter_widget.png" alt="marine-filter-widget" width="600"/> 

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/odourcollect-logo.png" alt="odourcollect-logo" width="75"/> OdourCollect widget 

The Odour Collect widget allows the user to get observations from the Odour Collect API. The widget looks like this:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/odour-collect-widget-2.png" alt="odour-collect-widget" width="350"/>

The widget has different search fields: date, annoy level, intensity level, category and type. Besides, the observations can be complemented with the distance from a Point of Interest, if this is set.

The output is a `Table` of observations, with this information:


| field           	| description 	|
|----------------	|------	|
| user              | OdourCollect's user ID of the citizen who registered the observation.      |
| date           	| Observation date in yyyy-mm-dd format.     	|
| time           	| Observation time in HH:mm (24h) format, UTC timezone.     	|
| week_day       	| Observation day of the week. This field is extra data calculated by pyodcollect to help the analyst in finding patterns. Please bear in mind that this calculation is based on UTC, not local time, so it could be misleading in some edge cases.|
| category       	| First tier of odour classification. In OdourCollect webapp, this is called "type". It provides complementary classification nuances that can be safely ignored for basic analysis. See the full table below for better understanding.  	|
| type           	| Second tier of odour classification. In OdourCollect webapp, this is called "subtype". It provides the richest odour classification criteria. See the full table below for better understanding.     	|
| hedonic_tone_n 	| Hedonic tone of odour observation (numeric representation). Hedonic tone is the subjective measurement of how annoying an odour is, from -4 (`Extremely unpleasant`) to +4 (`Extremely pleasant`). Zero is used to report neither annoyance nor pleasure. This scale is based on the `VDI 3940:2006` standard for odour impact assessment.       	|
| hedonic_tone_t 	| Text description version of the former metric.     	|
| intensity_n    	| Intensity of odour observation (numeric representation). Intensity is the measurement of how intense and noticeable an odour is, from 1 (`Very weak`) to 6 (`Extremely strong`). Zero (`Not perceptible`) is also used, but only to report the absence of odour in observations. This scale is based on the `VDI 3940:2006` standard for odour impact assessment.    	|
| intensity_t    	| Text description version of the former metric.     	|
| duration       	| Metric informing for how much time an odour has been perceived by a reporter. Categorical text data with the following self-explanatory options: `(No odour)`,`Punctual`,`Continuous in the last hour` and `Continuous throughout the day`       	|
| latitude       	| GPS coordinates of observation. Latitude.      	|
| longitude      	| GPS coordinates of observation. Longitude.     	|
| distance       	| Distance in Kms (with an accuracy of 0.01 Kms.) between the point of observation and a configurable Point of Interest (POI). This extra data is calculated by pyodcollect when the data analyst provides a set of coordinates for a given suspicious activity that motivates his/her analysis. In case no POI coordinates are provided, this field is missing.      	|
| time_hour           	| Observation time in HH (24h) format, UTC timezone.     	|
| time_mins           	| Observation time in mm (0-60') format, UTC timezone.     	|
| time_secs           	| Observation time in ss (0-60'') format, UTC timezone.     	|


## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_logo_gris.png" alt="canairio_logo.png" width="75"/> CanAIRio Fixed Stations
The widget allows to get observations from fixed stations through CanAIRio API. The widget looks like this:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_fixed_widget.png" alt="canairio_fixed_widget" width="300">

The widget filters between the different measurements and gets a dataframe with all data from fixed stations at the requested moment.

When selecting data from one of the stations, it can be combined with another widget (Last Hour Fixed Station) to get data from the last recorded data of this station.

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_fixed_last_hour.png" alt="canairio_fixed_widget" width="800">

The output of the Last Hour Fixed Station widget is a dataframe with the last registered measurements from this station.

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_logo_rosa.png" alt="canairio_logo.png" width="75"/> CanAIRio Mobile Stations

The widget gets observations from all the mobile stations registered by CanAIRio API.

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_mobile_widget.png" alt="canairio_fixed_widget" width="300">

The output can be placed on a map and coloured by any parameter:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_mobile_total.png" alt="canairio_fixed_widget" width="800">


We can select one device and get the complete track of the route using `Track - Mobile Station`. This is the result placed on a map:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_mobile_track.png" alt="canairio_fixed_widget" width="800">

The point can be coloured by any measurement.

This example can be loaded as a workflow (.ows format) directly in Orange Canvas:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_workflow.png" alt="canairio_fixed_widget" width="800">

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/inat-logo.png" alt="inaturalist-logo" width="75"/> INaturalist widget 

This widget collects observations from INaturalist API and allows filtering them by:

| Argument | Description | Example |
| --------- | ----------- | ------- |
| `Taxon` | One of the main taxonomies | `taxon=Aves` |
| `Taxon ID` | Number of a taxon | `taxon_id=14868` |
| `Project ID` | Number of a project | `project_id=80406` |
| `Place ID` | Name of a place | `place_id=200` |
| `User name` | Name of user who has uploaded the observations | `user="zolople"` |
| `Observation date` | Filters for observations date | `starts_on=2024-06-01` |
| `Creation date` | Filters for upload date | `since=2024-06-01` |
| `Research grade only` | Checkbox to select just research grade observations  | `research_grade=True` |
| `Max. number of results` | The max. number should be under 10,000 (API limit) | `num_max=800` |

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/inaturalist_filter.png" alt="inaturalist-widget" width="250"/>

The INaturalist widget integrates the Python library `mecoda-inat` into a visual interface. You can make any query and download two outputs, a dataframe with one observation per row and a dataframe with one photo per row. 

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/smartcitizen.png" alt="smartcitizen-logo" width="75"/> SmartCitizen widgets

The first widget (Smart Citizen Search) collects data from the Smart Citizen API. It allows you to select the device either via device ID (the number after https://smartcitizen.me/kits/[...]) or by searching the API by city, tags, or device type. The second widget (Smart Citizen Data) uses the data from the first one and collects time-series tabular data from a device, with a defined `rollup` (i.e. the frequency of the readings), minimum and maximum date; as well as resample options.

Example workflow is available at https://github.com/fablabbcn/smartcitizen-docs/blob/master/docs/assets/ows/example_sc.ows and documentation will be made available at https://docs.smartcitizen.me/Data/.

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/logo-aire-ciudadano.png" alt="aireciudadano-logo" width="75"/> Aire Ciudadano widget

The widget allows one to get data from Aire Ciudadano air quality stations, from the last registers or filtering by a range of time.

The output is a table with these columns:
| Field | Description |
| --------- | ----------- |
| `station` | Code of the station. |
| `date` | Date of registry in format `Year-Month-Date`. |
| `time` | Time of registry in format `Hour:Minute:Second`. |
| `Latitude` | Geographical latitude. |
| `Longitude` | Geographical longitude. |
| `CO2` | Value in ppm (parts per million) of the concentration of carbon dioxide. |
| `Humidity` | Value in % of relative humidity. |
| `InOut` | Variable to identify if the sensor is located outdoors (InOut= 0) or indoors (InOut = 1). |
| `NOx` | NOx index (nitrous oxides) with [range from 1 to 500](https://sensirion.com/media/documents/9F289B95/6294DFFC/Info_Note_NOx_Index.pdf), only applicable to [Sensirion's SEN55 sensor](https://sensirion.com/products/catalog/SEN55/). |
| `Noise` | Value in dbA (A-weighted decibel). |
| `NoisePeak` | Peak value in dbA reached in the time range (Publication time) in which the sensor publishes its data. |
| `PM10` | Value in ug/m3 of Particulate Matter PM10. |
| `PM25` | Value in ug/m3 of Particulate Matter PM2.5. |
| `PM252` | Value in ug/m3 of Particulate Matter PM2.5 measured by an installed secondary sensor (optional). |
| `PM25raw` | Value in ug/m3 of Particulate Matter PM2.5 without adjustment, only applies to Plantower brand sensors for which the "Plantower PMS adjust RECOMMENDED" function has been activated. |
| `Temperature` | Value in °C of the temperature. |
| `VOC` | VOC index (volatile organic compounds) with [range from 1 to 500](https://sensirion.com/media/documents/02232963/6294E043/Info_Note_VOC_Index.pdf), only applicable to [Sensirion SEN55 and SEN54 sensor](https://sensirion.com/products/catalog/SEN55/). |

# Testing
To run tests locally you'll need to have python 3.8, pip, virtualenv and git installed.

* Clone the repository and go into the directory:
```
git clone https://github.com/eosc-cos4cloud/mecoda-orange.git
cd mecoda-orange
```

* Set up the virtualenv for running tests:
```
virtualenv -p `which python3.8` env
source env/bin/activate
```

* Install mecoda-orange:
```
pip install -e .
```

* Install development dependencies:
```
pip install j-r requirements-dev.txt
```

* Run tests from the mecoda-orange directory:
```
pytest
```

* To run only one test,  use:
```
pytest -k <name-of-the-test>
```

# Next steps
MECODA is intended to be kept as an open-source repository. It will be ensured to be maintained, at least as part of other existing repositories. A version will be kept in [CSIC Gitlab](https://git.csic.es/).

# License
This repository is under GPLv3 license. See [license](./license) for more details.
