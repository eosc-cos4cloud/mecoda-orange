import pandas as pd
import os
import geopandas as gpd
from shapely.geometry import LineString
from geopy.geocoders import Nominatim
from geopandas.tools import sjoin
from mecoda_minka import get_obs, get_dfs
import fiona

from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui, widget
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame

from PyQt5.QtWidgets import QFileDialog
from AnyQt.QtWidgets import QStyle, QSizePolicy as Policy

# Enable fiona driver
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

class MapWidget(OWBaseWidget):
    
    # Widget's name as displayed in the canvas
    name = "Map Filter"

    # Short widget description
    description = "Filter observations located into an area, expressed as shapefile or link to Minka place"

    # An icon resource file path for this widget
    icon = "icons/globe-minka.png"

    # Priority in the section MECODA
    priority = 5

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    path_file = Setting("", schema_only=True)


    # Widget's outputs; here, a single output named "Observations", of type Table
    class Inputs:
        data = Input("Data", Orange.data.Table, auto_summary=False)

    class Outputs:
        observations = Output("Observations", Orange.data.Table, auto_summary=False)


    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(
            info, 
            ''
            )
        self.infob = gui.widgetLabel(info, '')

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(self.controlArea, "Source")

        file_button = gui.button(
            self.searchBox, 
            self, 
            'Choose .shp or .kml file',
            callback=self.browse_file, 
            autoDefault=False,
            width=350,
            )
        file_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        file_button.setSizePolicy(
            Policy.Maximum, 
            Policy.Fixed
            )

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Load", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Loading...')

    def browse_file(self):
        dialog = QFileDialog()
        home = os.path.expanduser("~")
        path_string, __ = dialog.getOpenFileName(
            self, 
            'Select a shp or kml file', 
            home, 
            "Map Files (*.kml *.shp)"
            )
        self.path_file = path_string

        if self.path_file is not None:
            try:
                self.infoa.setText(f"<b>File selected:</b><br>{path_string}")
                self.infob.setText("")

            except ValueError:
                self.infoa.setText(f'Nothing found.')
                
            except Exception as error:
                self.infoa.setText(f'ERROR: \n{error}')
                self.infob.setText("")
                print(error)
        else:
            self.infoa.setText(f'Choose some shape file to load data.')

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.input_data = table_to_frame(dataset)
            self.infoa.setText(f'{len(self.input_data)} instances in input dataset')
        return self.input_data

    def commit(self):
        self.infoa.setText(f'Loading...')
        self.infob.setText(f'(This could take a while, be patient)')
        try:
            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()
            
            print(len(self.input_data))
            if self.path_file != "":
                if ".shp" in self.path_file:
                    map_file = gpd.read_file(self.path_file)
                    #map_file.crs = {'init': 'epsg:4326'}
                if ".kml" in self.path_file:
                    map_file = gpd.read_file(self.path_file, driver='KML')
                    #map_file.crs = {'init': 'epsg:4326'}

                geo_data = gpd.GeoDataFrame(
                    self.input_data, 
                    geometry=gpd.points_from_xy(
                        self.input_data.longitude, 
                        self.input_data.latitude
                    )
                )
                geo_data = geo_data.set_crs('epsg:4326')

                #geo_data.crs = {'init': 'epsg:4326'}
                map_file = map_file.to_crs(4326)
                df_points = sjoin(geo_data, map_file)
                observations = self.input_data[self.input_data.id.isin(df_points.id)]
            
            if len(observations) > 0:
                self.infoa.setText(f'{len(observations)} observations gathered')
                self.infob.setText(f'')
                self.Outputs.observations.send(table_from_frame(observations))
                self.info.set_output_summary(len(observations))

            else:
                self.infoa.setText(f'Nothing found.')
                self.infob.setText(f'')
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')
            self.infob.setText(f'')
            
        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')
            self.infob.setText(f'')
            
        progress.finish()    
        

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(MapWidget).run()