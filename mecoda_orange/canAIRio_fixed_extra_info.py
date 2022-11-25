from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
import requests
import pandas as pd
from datetime import datetime


def get_historic_data_fixed_station(st) -> pd.DataFrame:
    url = f"http://api.canair.io:8080/dwc/stations/{st}"
    response = requests.get(url).json()
    data = pd.DataFrame(response)
    data = data.explode('measurements').reset_index(drop=True)
    for col in ['measurementID', 'measurementType', 'measurementUnit', 'measurementDeterminedDate ', 'measurementDeterminedBy', 'measurementValue']:
        data[col] = data['measurements'].str.get(col)
    data = data.drop(columns='measurements')

    data.rename(columns={
        'measurementDeterminedDate ': 'measurementDeterminedDate'}, inplace=True)
    cols = [
        'measurementDeterminedDate',
        'observedOn', 'measurementID']
    data[cols] = data[cols].apply(pd.to_datetime)
    return data


class ExtraInfoWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Last Hour Fixed Station"
    # Short widget description
    description = "Get extra information from fixed stations through CanAIRio API"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/circle-info-solid-gris.png"
    priority = 10

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # We want the current number entered by the user to be saved and restored when saving/loading a workflow.
    # We can achieve this by declaring a special property/member in the widget’s class definition like so:
    obs_table = Setting("", schema_only=True)

    # Inputs and Outputs
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

        else:
            self.dataset = None
            self.infoa.setText(
                'No data on input yet, waiting to get something.')
            self.infob.setText('')
        self.commit()

    def selection(self):
        if self.dataset is None:
            return
        df = table_to_frame(self.dataset)
        ids = df['station_name'].to_list()
        progress = gui.ProgressBar(self, len(df))

        observations = pd.DataFrame()
        for id_num in ids:
            obs = get_historic_data_fixed_station(id_num)
            observations = pd.concat([observations, obs])
            progress.advance()

        progress.finish()

        if len(df['measurementType'].unique()) == 1:
            observations = observations[observations['measurementType']
                                        == df['measurementType'].unique()]

        self.obs_table = table_from_frame(observations)

    def commit(self):
        if self.dataset is not None:

            df = table_to_frame(self.dataset)

            ids = df['station_name'].to_list()
            progress = gui.ProgressBar(self, len(df))
            observations = pd.DataFrame()
            for id_num in ids:
                obs = get_historic_data_fixed_station(id_num)
                observations = pd.concat([observations, obs])
                progress.advance()
            progress.finish()

            types = df['measurementType'].unique()
            for t in types:
                observations = observations[observations['measurementType'] == t]

            observations.measurementValue = observations.measurementValue.astype(
                float)
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
