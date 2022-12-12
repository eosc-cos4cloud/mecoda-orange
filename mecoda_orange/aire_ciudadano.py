
from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

import requests
import pandas as pd
import datetime
import numpy as np

# constant
selected_cols = [        
        "CO2",
        "Humidity",
        "InOut",
        "Latitude",
        "Longitude",
        "NOx",
        "Noise",
        "NoisePeak",
        "PM10",
        "PM25",
        "PM252",
        "PM25raw",
        "Temperature",
        "VOC",
        ]

# Get data from API
def get_data(url, selected_cols):
    data = requests.get(url).json()['data']['result']
    df = pd.json_normalize(data)

    # list of values or single value in data response
    if 'values' in df.columns:
        df = df.explode('values')
        df['date'] = df['values'].apply(lambda x: datetime.datetime.utcfromtimestamp(x[0]).date())
        df['time'] = df['values'].apply(lambda x: datetime.datetime.utcfromtimestamp(x[0]).time())
        df['value'] = df['values'].apply(lambda x: x[1])
        df = df.drop(columns="values")
    elif 'value' in df.columns:
        df['date'] = df['value'].apply(lambda x: datetime.datetime.utcfromtimestamp(x[0]).date())
        df['time'] = df['value'].apply(lambda x: datetime.datetime.utcfromtimestamp(x[0]).time())
        df['value'] = df['value'].apply(lambda x: x[1])
    
    df = df.rename(columns={
        "metric.__name__": "metric_name", 
        "metric.exported_job": "station",
        })
    
    # remove columns not used
    df = df.drop(columns=[col for col in df.columns if "metric." in col]).reset_index(drop=True)

    # remove rows with no station provided
    df = df[df['station'].notnull()]
    
    # convert df to wide table
    df_result = _wide_table(df, selected_cols)
    
    # set format and replace zero values in lat-lon columns
    for col in selected_cols:
        df_result[col] = df_result[col].astype(float)
    df_result['Latitude'].replace(0, np.nan, inplace=True)
    df_result['Longitude'].replace(0, np.nan, inplace=True)

    return df_result
    
# function to get wide table
def _wide_table(df, selected_cols):
    df_result = pd.pivot(
        df, 
        index=['station', 'date', 'time'], 
        columns='metric_name', 
        values='value'
        ).reset_index()

    df_result = df_result[
        ['station', 'date', 'time'] + selected_cols
        ].reset_index(drop=True)

    df_result.columns.name = ""

    return df_result

# constructor of the step value for time range queries
def _get_step(number, choice):
    # convert word to code
    options = {
        "seconds": "s",
        "minutes": "m",
        "hours": "h",
        "days": "d",
        "weeks": "w",
        "years": "y",
        }
    
    # construct expression for step
    step = f"{number}{options[choice]}"

    return step

class AireCiudadanoWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Aire Ciudadano"

    # Short widget description
    description = "Get registers from AireCiudadano API"

    # An icon resource file path for this widget
    icon = "icons/logo-aire-ciudadano.png"

    # Priority in the section MECODA
    priority = 20

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    option = Setting("", schema_only=True)
    starts_day = Setting(str(datetime.date.today()), schema_only=True)
    starts_hour = Setting("00:00", schema_only=True)
    ends_day = Setting(str(datetime.date.today()), schema_only=True)
    ends_hour = Setting("00:00", schema_only=True)
    step_number = Setting(1, schema_only=True)
    step_option = Setting("hours", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        registers = Output(
            "Registers", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(info, 'No registers fetched yet.')
        self.infob = gui.widgetLabel(info, '')
        
        # type of search area
        gui.separator(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Search options")
        gui.radioButtonsInBox(
            self.optionsBox, 
            self, 
            "option", 
            btnLabels=["Last register", "Time range"], 
            orientation=1,
            callback=self.option
            )
        
        # parameters area
        gui.separator(self.controlArea)
        self.parametersBox = gui.widgetBox(
            self.controlArea, 
            "Range options", 
            orientation=1,  
            disabled=True
            )

        self.startsBox = gui.widgetBox(self.parametersBox, "Starts", orientation=1)
        self.starts_day_line = gui.lineEdit(
            self.startsBox,
            self,
            "starts_day",
            label="<b>Day</b>",
            controlWidth=80
        )
        self.starts_hour_line = gui.lineEdit(
            self.startsBox,
            self,
            "starts_hour",
            label="<b>Hour</b>",
            controlWidth=40
        )

        self.endsBox = gui.widgetBox(self.parametersBox, "Ends", orientation=1)
        self.starts_day_line = gui.lineEdit(
            self.endsBox,
            self,
            "ends_day",
            label="<b>Day</b>",
            controlWidth=80
        )
        self.starts_hour_line = gui.lineEdit(
            self.endsBox,
            self,
            "ends_hour",
            label="<b>Hour</b>",
            controlWidth=40
        )

        self.stepBox = gui.widgetBox(
            self.parametersBox, 
            "Step", 
            orientation=2
            )
        self.step_number_line = gui.lineEdit(
            self.stepBox,
            self,
            "step_number",
            label="",
            controlWidth=80
        )
        self.step_options_line = gui.comboBox(
            self.stepBox,
            self,
            "step_option",
            box=None,
            label="",
            labelWidth=None,
            items=(
                "seconds", 
                "minutes", 
                "hours", 
                "days", 
                "weeks", 
                "years"
            ),
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=True,
            orientation=1,
        )

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Send", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')

    def option(self):
        # Enable time paramenters box when range is selected
        if self.option == 1:
            self.parametersBox.setDisabled(False)
        elif self.option == 0:
            self.parametersBox.setDisabled(True)
            

    def commit(self):
        self.infoa.setText("Searching...")
        self.infob.setText("")
        try:
            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()

            # query to get all data
            query = '{job%3D"pushgateway"}'

            # last registers selected
            if self.option == 0:
                url = f"http://sensor.aireciudadano.com:30887/api/v1/query?query={query}"

            # range of time selected
            elif self.option == 1:
                # construct start_datetime
                start_datetime = f"{self.starts_day}T{self.starts_hour}:00Z"

                # construct end_datetime
                end_datetime = f"{self.ends_day}T{self.ends_hour}:00Z"

                # construct step                
                step = _get_step(self.step_number, self.step_option)
                
                url = f"http://sensor.aireciudadano.com:30887/api/v1/query_range?query={query}&start={start_datetime}&end={end_datetime}&step={step}"
            
            # get obs from API, using the url created before
            obs = get_data(url, selected_cols)

            # convert to Table format for Orange environment
            table_obs = table_from_frame(obs)

            self.infoa.setText(
                f'{len(obs):,} registers gathered')
            self.info.set_output_summary(len(obs))
            self.Outputs.registers.send(table_obs)

        except ValueError:
            self.infoa.setText(f'Nothing found.')

        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')

        progress.finish()


# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(AireCiudadanoWidget).run()
