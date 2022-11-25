from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
import requests
import pandas as pd
from datetime import datetime


def get_mobile_track(name):
    try:
        df = pd.DataFrame(requests.get(
            f"http://api.canair.io:8080/tracks/{name}").json()['data'])
        df['station'] = name
        df['station'] = pd.Categorical(df['station'])
        df['timestamp'] = df.timestamp.apply(
            lambda x: datetime.fromtimestamp(x))
    except:
        print(f"Fallo: {name}")
        df = pd.DataFrame()
    return df


class ExtraInfoWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Track - Mobile Station"
    # Short widget description
    description = "Get extra information from mobile station tracks through CanAIRio API"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/circle-info-solid-rosa.png"
    priority = 12

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # We want the current number entered by the user to be saved and restored when saving/loading a workflow.
    # We can achieve this by declaring a special property/member in the widget’s class definition like so:
    #id_obs = Setting(0, schema_only=True)
    obs_table = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Number", of type int
    class Inputs:
        data = Input("Data", Orange.data.Table, auto_summary=False)

    class Outputs:
        extra_data = Output("extra", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()
        self.dataset = None

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(info, 'No observations fetched yet.')
        self.infob = gui.widgetLabel(info, '')

        gui.separator(self.controlArea)

    def info_searching(self):
        self.infoa.setText('Searching...')

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.dataset = dataset
            self.infoa.setText('%d instances in input dataset' % len(dataset))
            self.infob.setText("")

        else:
            self.dataset = None
            self.infoa.setText(
                'No data on input yet, waiting to get something.')
            self.infob.setText('')

        self.commit()

    def commit(self):
        if self.dataset is not None:
            df = table_to_frame(self.dataset)

            ids = df['name'].to_list()
            progress = gui.ProgressBar(self, len(df))

            observations = pd.DataFrame()
            for id_num in ids:
                obs = get_mobile_track(id_num)
                observations = pd.concat([observations, obs])
                progress.advance()
            progress.finish()

            self.obs_table = table_from_frame(observations)

            self.infoa.setText(
                f'{len(self.dataset)} instances in input dataset')
            self.infob.setText(
                f"{len(self.obs_table)} instances in output dataset")
            self.info.set_output_summary(len(observations))
        else:
            self.infoa.setText(
                'No data on input yet, waiting to get something.')
            self.infob.setText('')
            self.info.set_output_summary(self.info.NoOutput)

        self.Outputs.extra_data.send(self.obs_table)


if __name__ == "__main__":
    WidgetPreview(ExtraInfoWidget).run()
