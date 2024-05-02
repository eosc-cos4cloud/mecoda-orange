# <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/share.png" alt="mecoda-logo" width="100"/> Mecoda-Orange 

This repository includes different Orange Data Mining widgets to access data from [Minka](https://minka-sdg.org/), [Odour Collect](https://odourcollect.eu/), [canAIRio](https://canair.io/), [Ictio](https://ictio.org/), [Natusfera](https://natusfera.gbif.es/) or [Smart Citizen](https://smartcitizen.me).

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/cos4cloud.png" alt="cos4cloud-logo" width="75"/> MECODA is part of [Cos4Cloud](https://cos4cloud.eu/), a European Horizon 2020 project to boost citizen science technologies.

To use MECODA package you need to install Orange Data Mining platform through https://orangedatamining.com/download

Once Orange is installed, inside the Options menu, it's possible to get the package using "Add-ons" category, clicking on "Add more" and searching by name "mecoda-orange". The last version of the package will be installed into Orange platform.

You can find also a ["Installation Guide" and "Example of Use"](https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/docs/installation_and_user_guide.md).

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka-logo.png" alt="minka-logo" width="75"/> Minka widget 

This widget collects observations from Minka API and allows filter them by:

| Argument | Descrition | Example |
| --------- | ----------- | ------- |
| `Search by words` | Word or phrase found in the data of an observation | `query="quercus quercus"` |
| `Project name` | Name of a project | `project_name="urbamar"` |
| `User name` | Name of user who has uploaded the observations | `user="zolople"` |
| `Place` | One of the places created in minka website | `place="246: BioPrat"` |
| `Taxon` | One of the main taxonomies | `taxon="fungi"` |
| `Year` | Year of observations | `year=2019` |
| `Id of observation` | Identification number of a specific observation | `id_obs=425` |
| `Max. number of results` | The max. number should be under 20.000 (API limit) | `num_max=800` |

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
* **identifications_count**: number of identifications for a observation.
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

This widget takes a `Table` with observations (and a column with ids from Minka) and get the photos from all of them. Works with data from Minka Widget. 

The output is a Table with an image type feature that can be accessed using `Image viewer`.

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/arrow-down-wide-short-solid-minka.png" alt="taxon-filter" width="50"/> Minka Taxon Filter

This widget allows the user to filter Minka observations by different taxonomic levels (from kingdom to species). The levels shown are just the ones with registered observations.

The widget looks like that:
### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka_taxon_filter_2.png" alt="taxon-filter-widget" width="350"/> 

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/leaf-solid-minka.png" alt="taxon-filter-by-words" width="50"/> Minka Taxon Search

This widget allows the user to filter Minka observations by scientific or common name.

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/minka_taxon_search_widget.png" alt="taxon-search-widget" width="350"/> 

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/fish-minka.png" alt="fish-minka.png" width="50"/> Marine and Terrestrial Filter

The widget splits Table of observations into two dataframes: one for marine species and other for terrestrial ones. Just gets observations with research degree.

### <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/marine_filter_widget.png" alt="marine-filter-widget" width="600"/> 

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/odourcollect-logo.png" alt="odourcollect-logo" width="75"/> OdourCollect widget 

The Odour Collect widget allows the user to get observations from Odour Collect API. The widget looks like this:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/odour-collect-widget-2.png" alt="odour-collect-widget" width="350"/>

The widget has different search fields: date, annoy level, intensity level, category and type. Besides, the observations can be complemented with the distance from a Point of Interest, if this is set.

The output is a `Table` of observations, with this information:


| field           	| description 	|
|----------------	|------	|
| user              | OdourCollect's user ID of the citizen that registered the observation.      |
| date           	| Observation date in yyyy-mm-dd format.     	|
| time           	| Observation time in HH:mm (24h) format, UTC timezone.     	|
| week_day       	| Observation day of week. This field is extra data calculated by PyOdourCollect to help the analyst in finding patterns. Please bear in mind that this calculation is based on UTC, not local time, so it could be misleading in some edge cases.|
| category       	| First tier of odour classification. In OdourCollect webapp, this is called "type". It provides complementary classification nuances that can be safely ignored for basic analysis. See the full table below for better understanding.  	|
| type           	| Second tier of odour classification. In OdourCollect webapp, this is called "subtype". It provides the richest odour classification criteria. See the full table below for better understanding.     	|
| hedonic_tone_n 	| Hedonic tone of odour observation (numeric representation). Hedonic tone is the subjective measurement of how annoyant an odour is, from -4 (`Extremely unpleasant`) to +4 (`Extremely pleasant`). Zero is used to report nor annoyance nor pleasure. This scale is based on the `VDI 3940:2006` standard for odour impact assessement.       	|
| hedonic_tone_t 	| Text description version of the former metric.     	|
| intensity_n    	| Intensity of odour observation (numeric representation). Intensity is the measurement of how intense and noticeable an odour is, from 1 (`Very weak`) to 6 (`Extremely strong`). Zero (`Not perceptible`) is also used, but only to report absence of odour in observations. This scale is based on the `VDI 3940:2006` standard for odour impact assessement.    	|
| intensity_t    	| Text description version of the former metric.     	|
| duration       	| Metric informing for how much time an odour has been perceived by reporter. Categorical text data with following self-explanatory options: `(No odour)`,`Punctual`,`Continuous in the last hour` and `Continuous throughout the day`       	|
| latitude       	| GPS coordinates of observation. Latitude.      	|
| longitude      	| GPS coordinates of observation. Longitude.     	|
| distance       	| Distance in Kms (with an accuracy of 0.01 Kms.) between the point of observation and a configurable Point of Interest (POI). This extra data is calculated by PyOdourCollect when the data analyst provides a set of coordinates for a given suspicious activity that motivates his/her analysis. In case that no POI coordinates are provided, this field is missing.      	|
| time_hour           	| Observation time in HH (24h) format, UTC timezone.     	|
| time_mins           	| Observation time in mm (0-60') format, UTC timezone.     	|
| time_secs           	| Observation time in ss (0-60'') format, UTC timezone.     	|


## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_logo_gris.png" alt="canairio_logo.png" width="75"/> CanAIRio Fixed Stations
The widget allows to get observations from fixed stations through CanAIRio API. The widget looks like this:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_fixed_widget.png" alt="canairio_fixed_widget" width="300">

The widget filters between the different measurements and gets a dataframe with all data from fixed stations at the request moment.

When selecting data from one of the stations, it can be combined with another widget (Last Hour Fixed Station) to get data from the last recorded data of this station.

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_fixed_last_hour.png" alt="canairio_fixed_widget" width="800">

The output of Last Hour Fixed Station widget is a dataframe with last registered measurements from this station.

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_logo_rosa.png" alt="canairio_logo.png" width="75"/> CanAIRio Mobile Stations

The widget gets observations from all the mobile stations registered by CanAIRio API.

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_mobile_widget.png" alt="canairio_fixed_widget" width="300">

The output can be placed in a map and colored by any parameter:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_mobile_total.png" alt="canairio_fixed_widget" width="800">


We can select one device and get the complete track of the route using `Track - Mobile Station`. This is the result placed in a map:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_mobile_track.png" alt="canairio_fixed_widget" width="800">

The point can be coloured by any measurement.

This example can be loaded as a workflow (.ows format) directly in Orange Canvas:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/canairio_workflow.png" alt="canairio_fixed_widget" width="800">

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/ictio-circular.png" alt="ictio_logo.png" width="75"/> Ictio widget

The widget analyse data from [Ictio's citizen observatory](https://ictio.org/) for Amazon basin fish observation. The data from this Citizen Observatory is not freely available via public API nor public download, but it can be downloaded as a zip file after registration in web page.

This widget takes an Ictio_Basic zip file from ictio.org and process it using [IctioPy](https://github.com/ScienceForChange/IctioPy) library, created by Science For Change:

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/ictio_widget.png" alt="ictio_widget" width="300">

The output of this widget is a `Table` with this structure:

* `obs_id`: Unique observation ID.
* `weight`: Total weight in Kg reported for the given taxon.
* `price_local_currency`: Price per Kg in the local currency for the taxon.
* `obs_comments`: Comments made by the Citizen Scientist at the time of registering the observation.
* `upload_date_yyyymmdd`: Date of observation upload. It does not necessarily match observation date. The relevant data for analysis purposes is the observation date.
num_photos: Number of photos taken with the observation. The photos are not available in the basic version of the ictio.org's database, so this field is only included as a reference.
* `user_id`: Anonymous, numeric ID of the user that made the observation.
checklist_id: Unique checklist identifier
* `protocol_name`: Name of the observation protocol used. Possible values: During fishing event , After the fishing event, Market Survey and Port Survey.
complete_checklist: Indicates if the checklist was completed. A complete checklist is when all taxa caught during the fishing effort are reported. In a market survey it would be all taxa observed at the market. If observation was made via app, it is assumed that user reported a complete checklist.
* `fishing_duration`: The duration of the fishing effort in hours.
submission_method: How was data submitted? EFISH_android for mobile app or EFISH_upload for upload tool.
* `app_version`: Version of the mobile app or upload tool used.
* `taxon_code`: Species taxon code.
* `scientific_name`: Scientific name of the species observed.
* `num_of_fishers`: Number of fishers participating in fishing effort.
* `number_of_fish`: Number of individual fish reported for the given taxon.
* `obs_year`: Year of observation.
* `obs_month`: Month of observation.
* `obs_day`: Day of month of observation.
* `port`: This is the name of the port where data was collected and is only reported with the Port Protocol. This is not the location where fish were caught.
* `location_type`: Ictio has three location types: Watersheds, Ictio Hotspots, and Personal Locations. This field will identify watersheds and Ictio Hotspots. This field will be null for personal locations. A personal location is any new location added with the upload tool or based on raw GPS coordinates.
* `country_code`: Country Code, automatically assigned by latitude and longitude. If you assign a checklist to a watershed it will be assigned to the country where the centroid of the watershed is. If the watershed overlaps a boundary, it could be assigned to a different country from where it is being submitted.
* `country_name`: Country in which the observation was made.
* `state_province_code`: State/Province Code, automatically assigned by latitude and longitude. If you assign a checklist to a watershed it will be assigned to the State/Province where the centroid of the watershed is. If the watershed overlaps a boundary, it could be assigned to a different State/Province.
* `state_province_name`: State/Province name, automatically assigned by latitude and longitude. If there is a checklist assigned to a watershed, observation will be assigned to the State/Province where the centroid of the watershed is. If the watershed overlaps a boundary, it could be assigned to a different State/Province.
watershed_code: Unique identifier for watershed. For Ictio hotspots and personal locations, the watershed code and watershed name are inferred based on geographic position of Citizen Scientist at the time of observation.
* `watershed_name`: Name of the watersed in which the osbervation was made.

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/natusfera_v1.png" alt="natusfera-logo" width="75"/> Natusfera widget 

This widget collects observations from Natusfera API and allows filter them by:

| Argument | Descrition | Example |
| --------- | ----------- | ------- |
| `Search by words` | Word or phrase found in the data of an observation | `query="quercus quercus"` |
| `Project name` | Name of a project | `project_name="urbamar"` |
| `User name` | Name of user who has uploaded the observations | `user="zolople"` |
| `Place` | Name of a place | `place_name="Barcelona"` |
| `Taxon` | One of the main taxonomies | `taxon="fungi"` |
| `Year` | Year of observations | `year=2019` |
| `Id of observation` | Identification number of a specific observation | `id_obs=425` |
| `Max. number of results` | The max. number should be under 20.000 (API limit) | `num_max=800` |

<img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/natusfera-widget-2.png" alt="natusfera-widget" width="250"/>

The Natusfera widget integrates the Python library `mecoda-nat` into a visual interface. 
You can make any query and download two outputs, a dataframe with one observation per row and a dataframe with one photo per row. 
A single observation can have more than a photo.

## <img src="https://github.com/eosc-cos4cloud/mecoda-orange/blob/master/mecoda_orange/icons/smartcitizen.png" alt="smartcitizen-logo" width="75"/> SmartCitizen widgets

The first widget (Smart Citizen Search) collects data from the Smart Citizen API. It allows to select the device either via device ID (the number after https://smartcitizen.me/kits/[...]) or by searching the API by city, tags, or device type. The second widget (Smart Citizen Data) uses the data from the first one and collects timeseries tabular data from a device, with a defined `rollup` (i.e. the frequency of the readings), minimum and maximum date; as well as resample options.

Example workflow is available https://github.com/fablabbcn/smartcitizen-docs/blob/master/docs/assets/ows/example_sc.ows and documentation will be made available in https://docs.smartcitizen.me/Data/.

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

* Install pytest:
```
pip install pytest
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
MECODA is intented to be kept as an open source repository. It will be ensured to be maintained, at least as part of other existent repository. A version will be kept in [CSIC Gitlab](https://git.csic.es/).

# License
This repository is under GPLv3 license. See [license](./license) for more details.
