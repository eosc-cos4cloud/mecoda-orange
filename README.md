
# <img src="mecoda_orange/icons/share.png" alt="mecoda-logo" width="100"/> Mecoda-Orange 

Orange Data Mining Widgets to analyse data from science citizen observatories.

This repository includes different Orange Data Mining widgets to access data from Natusfera and Odour Collect APIs. 

## <img src="mecoda_orange/icons/natusfera_v1.png" alt="natusfera-logo" width="100"/> Natusfera widget 

The widget collect observations from Natusfera API and allows filter them by:

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

<img src="mecoda_orange/icons/natusfera-widget-2.png" alt="natusfera-widget" width="250"/>

The Natusfera widget integrates the Python library `mecoda-nat` into a visual interface. 
You can make any query and download two outputs, a dataframe with one observation per row and a dataframe with one photo per row. 
A single observation can have more than a photo. 

The `observations` table allows statistical analysis. The photos table allows image analysis.

The widget is complemented with two other widgets that can take input from it:

### <img src="mecoda_orange/icons/camera.png" alt="get-images" width="50"/> get_images

This widget takes a `Table` with observations (and a column with ids from Natusfera) and get the photos from all of them. 
Works with data from Natusfera API.

The output is a Table with an image type feature that can be accessed using `Image viewer`.

### <img src="mecoda_orange/icons/circle-info-solid.svg" alt="extra-info" width="50"/> extra_info

This widget takes a `Table` with observations (and a column with ids from Natusfera) and get extra information from Natusfera observations.


## <img src="mecoda_orange/icons/odourcollect-logo.png" alt="odourcollect-logo" width="100"/> OdourCollect widget 

The Odour Collect widget allows to get observations from Odour Collect API. The widget looks like this:

<img src="mecoda_orange/icons/odour-collect-widget-2.png" alt="odour-collect-widget" width="250"/>

The widget has different search fields: by date, by annoy level, by intensity level, by category and type. 
And also the observations can be complemented with the distance from a Point of Interest, if this is set.

The output is a `Table` of observations.


