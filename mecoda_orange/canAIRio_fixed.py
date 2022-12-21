
import pandas as pd
import requests
from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame


# Fixed stations
def get_fixed_stations_data(filter=None) -> pd.DataFrame:
    url = "http://api.canair.io:8080/dwc/stations"
    stations = requests.get(url).json()
    df_stations = pd.DataFrame(stations)
    # flat table
    df_stations = df_stations.explode('measurements').reset_index(
        drop=True).explode('measurements').reset_index(drop=True)
    for col in [
        'measurementID',
        'measurementType',
        'measurementUnit',
        'measurementDeterminedDate',
        'measurementDeterminedBy',
        'measurementValue'
    ]:
        df_stations[col] = df_stations['measurements'].str.get(col)
    df_stations = df_stations.drop(columns='measurements')
    df_stations['observedOn'] = pd.to_datetime(df_stations['observedOn'])
    df_stations.station_name = pd.Categorical(df_stations.station_name)
    if filter is not None:
        if filter != "":
            df_stations = df_stations[df_stations['measurementType'] == filter]
            df_stations.measurementValue = df_stations.measurementValue.astype(
                float)
    return df_stations


class CanairioWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "CanAIRio Fixed"

    # Short widget description
    description = "Get observations from fixed stations through CanAIRio API"

    # An icon resource file path for this widget
    icon = "icons/canairio_logo_gris.png"

    # Priority in the section MECODA
    priority = 9

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    type = Setting('', schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        observations = Output(
            "Observations", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(info, 'No observations fetched yet.')
        self.infob = gui.widgetLabel(info, '')

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")

        self.type_line = gui.comboBox(
            self.searchBox,
            self,
            "type",
            box=None,
            label="Measurement type:",
            labelWidth=None,
            items=(
                '',
                'PM1',
                'PM2.5',
                'PM10',
                'Temperature',
                'Humidity',
                'Pressure',
                'CO2',
                'CO2 Temperature',
                'CO2 Humidity'
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
        gui.button(self.commitBox, self, "Commit", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')

    def commit(self):
        self.infoa.setText(f'Searching...')
        self.infob.setText(f'')
        try:
            if self.type == "":
                self.type is None

            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()

            observations = get_fixed_stations_data(self.type)

            if len(observations) > 0:

                table_canairio = table_from_frame(observations)

                self.infoa.setText(
                    f'{len(observations)} observations gathered')
                self.info.set_output_summary(len(observations))

                self.Outputs.observations.send(table_canairio)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')

        except Exception as error:
            #self.infoa.setText(f'ERROR: \n{error}')
            self.infoa.setText(f'CanAIRio API is temporarily unavailable')
        progress.finish()


# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(CanairioWidget).run()
