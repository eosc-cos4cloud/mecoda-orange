from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
import pandas as pd
import requests

taxon_url = "https://raw.githubusercontent.com/eosc-cos4cloud/mecoda-orange/master/mecoda_orange/data/taxon_tree_with_marines.csv"
taxon_tree = pd.read_csv(taxon_url)


def get_marine(taxon_name):
    name_clean = taxon_name.replace(" ", "+")
    status = requests.get(
        f"https://www.marinespecies.org/rest/AphiaIDByName/{name_clean}?marine_only=true").status_code
    if (status == 200) or (status == 206):
        result = True
    else:
        result = False
    return result


class MarineWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Marine and Terrestrial Filter"
    # Short widget description
    description = "Splits Table of observations into two dataframes: one for marine species and other for terrestrial ones."

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/fish-minka.png"
    priority = 5

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Inputs and outputs
    class Inputs:
        data = Input("Data", Orange.data.Table, auto_summary=False)

    class Outputs:
        marines = Output("marines", Orange.data.Table, auto_summary=False)
        terrestrials = Output(
            "terrestrials", Orange.data.Table, auto_summary=False)

    def __init__(self):
        super().__init__()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, 'No data on input yet, waiting to get something.')
        self.infob = gui.widgetLabel(
            box, 'Just filter research quality grade observations.')

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText(f'{len(dataset)} instances in input dataset')
            df = table_to_frame(dataset)
            df['taxon_id'] = df.taxon_id.astype(int)
            progress = gui.ProgressBar(self, len(df))
            marine_df = taxon_tree[['taxon_id', 'rank', 'marine']]

            df_complete = df.merge(marine_df, how="left", on="taxon_id")

            df = df_complete[df_complete['quality_grade'] == "research"]

            marines_df = df[df.marine == True]
            terrestrials_df = df[df.marine == False]

            marines = table_from_frame(marines_df)
            terrestrials = table_from_frame(terrestrials_df)

            self.infoa.setText(f'Marines: {len(marines)}')
            self.infob.setText(f'Terrestrials: {len(terrestrials)}')

            self.Outputs.marines.send(marines)
            self.Outputs.terrestrials.send(terrestrials)

            progress.finish()

        else:
            self.infoa.setText(
                'No data on input yet, waiting to get something.')
            self.infob.setText('')


if __name__ == "__main__":
    WidgetPreview(MarineWidget).run()
