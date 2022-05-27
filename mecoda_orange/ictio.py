import pandas as pd
import os
from ictiopy import ictiopy

from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui, widget
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

from PyQt5.QtWidgets import QFileDialog
from AnyQt.QtWidgets import QStyle, QSizePolicy as Policy

def clean_df(observations):
    observations.obs_id = pd.Categorical(observations.obs_id)
    observations.weight = observations.weight.astype(float)
    observations.price_local_currency = observations.price_local_currency.astype(float)
    observations.upload_date_yyyymmdd = pd.Categorical(observations.upload_date_yyyymmdd.astype(int))
    observations.num_photos = observations.num_photos.astype(int)
    observations.checklist_id = pd.Categorical(observations.checklist_id)
    observations.protocol_name = pd.Categorical(observations.protocol_name)
    observations.fishing_duration = observations.fishing_duration.astype(float)
    observations.submission_method = pd.Categorical(observations.submission_method)
    observations.app_version = pd.Categorical(observations.app_version)
    observations.taxon_code = pd.Categorical(observations.taxon_code)
    observations.scientific_name = pd.Categorical(observations.scientific_name)
    observations.num_of_fishers = observations.num_of_fishers.astype(float)
    observations.number_of_fish = observations.number_of_fish.astype(float)
    observations.obs_year = observations.obs_year.astype(int)
    observations.obs_month = observations.obs_month.astype(int)
    observations.obs_day = observations.obs_day.astype(int)
    observations.port = pd.Categorical(observations.port)
    observations.location_type = pd.Categorical(observations.location_type)
    observations.country_code = pd.Categorical(observations.country_code)
    observations.country_name = pd.Categorical(observations.country_name)
    observations.state_province_code = pd.Categorical(observations.state_province_code)
    observations.state_province_name = pd.Categorical(observations.state_province_name)
    observations.watershed_code = pd.Categorical(observations.watershed_code)
    observations.watershed_name = pd.Categorical(observations.watershed_name)
    
    return observations



class IctioWidget(OWBaseWidget):
    
    # Widget's name as displayed in the canvas
    name = "Ictio Observations"

    # Short widget description
    description = "Get observations from Ictio, a mobile phone app created to register observations of caught fish in the Amazon basin"

    # An icon resource file path for this widget
    icon = "icons/ictio-circular.png"

    # Priority in the section MECODA
    priority = 10

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    path = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        observations = Output("Observations", Orange.data.Table, auto_summary=False)

    """UserAdviceMessages = [
        widget.Message(
            "This module takes an "
            "Ictio_Basic zip file from ictio.org",
            ""),
        widget.Message(
            "This module takes an "
            "Ictio_Basic zip file from ictio.org",
            ""
        )
    ]"""

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        #layout = QGridLayout()
        #layout.setSpacing(4)

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(
            info, 
            'Please specify the path to a <b>Ictio_Basic_xxxxxxxx.zip</b> file <br>that has been downloaded from the "Download" section<br> of <a href="https://ictio.org/">ictio.org</a> website.'
)
        self.infob = gui.widgetLabel(info, 'NOTE: Downloading the file requires user registration.')

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(self.controlArea, "Source")


        #dialog = QFileDialog()
        #path, __ = dialog.getOpenFileName(self, 'Select a zip file')
        
        #print(path)

        file_button = gui.button(
            self.searchBox, 
            self, 
            'Choose .zip', 
            callback=self.browse_file, 
            autoDefault=False,
            width=325,
            )
        file_button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        file_button.setSizePolicy(
            Policy.Maximum, 
            Policy.Fixed
            )
        #layout.addWidget(file_button, 0, 2)

        """self.path_line = gui.lineEdit(
            self.searchBox, 
            self, 
            "path", 
            label="Path to zip:", 
            orientation=1, 
            controlWidth=300,
            disable=True
            )"""

        gui.separator(self.searchBox)

        # commit area, not included
        #self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        #gui.button(self.commitBox, self, "Load", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Loading...')

    def browse_file(self):
        dialog = QFileDialog()
        home = os.path.expanduser("~")
        path_string, __ = dialog.getOpenFileName(self, 'Select a zip file', home, "Zip files (*.zip)")
        self.path = path_string

        self.infoa.setText(f'Loading...')
        self.infob.setText(f'(This could take a while, be patient)')

        if "Ictio" in self.path:
            try:
                # show progress bar
                progress = gui.ProgressBar(self, 2)
                progress.advance()
                
                observations = ictiopy.load_zipdb(self.path) 
                observations = clean_df(observations)

                if len(observations) > 0:
                    
                    table_ictio = table_from_frame(observations)

                    self.infoa.setText(f'{len(observations)} observations gathered')
                    self.infob.setText("")

                    self.info.set_output_summary(len(observations))

                    self.Outputs.observations.send(table_ictio)

                else:
                    self.infoa.setText(f'Nothing found.')
                    self.info.set_output_summary(self.info.NoOutput)

            except ValueError:
                self.infoa.setText(f'Nothing found.')
                
            except Exception as error:
                self.infoa.setText(f'ERROR: \n{error}')
                self.infob.setText("")
                print(error)
                
            progress.finish()

        elif self.path == "":
            self.infoa.setText(f'Choose some zip file to load data.')
        else:
             self.infoa.setText(f'ERROR: \nNot suitable zip file') 
             self.infob.setText("File name should be Ictio_Basic_YYYYMMDD.zip")

    def commit(self):
        self.infoa.setText(f'Loading...')
        self.infob.setText(f'(This could take a while, be patient)')
        try:
            # convert date_init and date_end to datetime format

            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()
            
            observations = ictiopy.load_zipdb(self.path) 
            observations = clean_df(observations)

            if len(observations) > 0:
                
                table_ictio = table_from_frame(observations)

                self.infoa.setText(f'{len(observations)} observations gathered')
                self.infob.setText("")

                self.info.set_output_summary(len(observations))

                self.Outputs.observations.send(table_ictio)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')
            
        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')
            self.infob.setText("")
            print(error)
            
        progress.finish()    
        

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(IctioWidget).run()