
from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame
import pandas as pd
import requests

# Mobile stations


def get_mobile_stations():
    url = "http://api.canair.io:8080/tracks"
    stations = requests.get(url, verify=False).json()
    df_stations = pd.DataFrame(stations).transpose()
    for col in [
        'P10',
        'P25',
        'alt',
        'spd'
    ]:
        df_stations[col] = df_stations['lastSensorData'].str.get(col)
    df_stations = df_stations.drop(columns='lastSensorData')

    #df_stations['index'] = pd.Categorical(df_stations['index'])
    df_stations['name'] = pd.Categorical(df_stations['name'])
    df_stations['deviceId'] = pd.Categorical(df_stations['deviceId'])
    df_stations.rename(columns=lambda s: s.replace(
        "lastSensorData.", ""), inplace=True)

    df_stations.lastLat = df_stations.lastLat.astype(float)
    df_stations.lastLon = df_stations.lastLon.astype(float)
    df_stations['size'] = df_stations["size"].astype(int)
    df_stations[[
        'P10',
        'P25',
        'alt',
        'spd'
    ]] = df_stations[[
        'P10',
        'P25',
        'alt',
        'spd'
    ]].astype(float)
    return df_stations


class CanairioWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "CanAIRio Mobile"

    # Short widget description
    description = "Get observations from mobile stations through CanAIRio API"

    # An icon resource file path for this widget
    icon = "icons/canairio_logo_rosa.png"

    # Priority in the section MECODA
    priority = 11

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings

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

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Commit", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')

    def commit(self):
        self.infoa.setText(f'Searching...')
        self.infob.setText(f'')
        try:
            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()

            observations = get_mobile_stations()

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
