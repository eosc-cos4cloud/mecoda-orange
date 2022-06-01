import pandas as pd
import os
import datetime
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
    observations.weight = observations.weight.astype(float)
    observations.price_local_currency = observations.price_local_currency.astype(float)
    observations.num_photos = observations.num_photos.astype(int)
    observations.fishing_duration = observations.fishing_duration.astype(float)
    observations.num_of_fishers = observations.num_of_fishers.astype(float)
    observations.number_of_fish = observations.number_of_fish.astype(float)
    observations.obs_year = observations.obs_year.astype(int)
    observations.obs_month = observations.obs_month.astype(int)
    observations.obs_day = observations.obs_day.astype(int)
    return observations

def split_date(observations, init, end):
    observations['obs_date'] = observations['obs_year'].astype(int).astype(str) + observations['obs_month'].astype(int).astype(str).str.zfill(2) + observations['obs_day'].astype(int).astype(str).str.zfill(2)
    observations['obs_date'] = pd.to_datetime(observations['obs_date'])
    observations = observations[observations['obs_date'] >= init]
    observations = observations[observations['obs_date'] <= end]
    observations = observations.drop(['obs_date'], axis=1)
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
    date_init = Setting("1860-01-01", schema_only=True)
    date_end = Setting(str(datetime.date.today()), schema_only=True)
    #observations = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        observations = Output("Observations", Orange.data.Table, auto_summary=False)


    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

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

        #gui.separator(self.searchBox)
        self.dateBox = gui.widgetBox(self.controlArea, "Filter by date")

        self.date_init_line = gui.lineEdit(
            self.dateBox, 
            self, 
            "date_init", 
            label="Initial Date:", 
            orientation=1, 
            controlWidth=140,
            )

        self.date_end_line = gui.lineEdit(
            self.dateBox, 
            self, 
            "date_end", 
            label="End Date:", 
            orientation=1, 
            controlWidth=140
            )

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Load", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Loading...')

    def browse_file(self):
        dialog = QFileDialog()
        home = os.path.expanduser("~")
        path_string, __ = dialog.getOpenFileName(self, 'Select a zip file', home, "Zip files (*.zip)")
        self.path = path_string

        if self.path is not None:
            try:
                file_selected = path_string.split("data")[-1]
                self.infoa.setText(f"<b>File selected:</b><br>{file_selected}")
                self.infob.setText("")

            except ValueError:
                self.infoa.setText(f'Nothing found.')
                
            except Exception as error:
                self.infoa.setText(f'ERROR: \n{error}')
                self.infob.setText("")
                print(error)

        else:
            self.infoa.setText(f'Choose some zip file to load data.')
        """else:
             self.infoa.setText(f'ERROR: \nNot suitable zip file') 
             self.infob.setText("File name should be Ictio_Basic_YYYYMMDD.zip")"""

    def commit(self):
        self.infoa.setText(f'Loading...')
        self.infob.setText(f'(This could take a while, be patient)')
        try:
            # convert date_init and date_end to datetime format
            if type(self.date_init) == str:
                init = datetime.datetime.strptime(self.date_init, '%Y-%m-%d')
            else:
                init = self.date_init

            if type(self.date_end) == str:
                end = datetime.datetime.strptime(self.date_end, '%Y-%m-%d')
            else:
                end = self.date_end

            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()
            
            observations = ictiopy.load_zipdb(self.path) 
            observations = clean_df(observations)
            observations = split_date(observations, init, end)

            if len(observations) > 0:
                
                table_ictio = table_from_frame(observations)

                self.infoa.setText(f'{len(observations):,} observations gathered')
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