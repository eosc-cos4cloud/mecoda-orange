from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
from mecoda_minka import get_obs, get_dfs
import requests 
import numpy as np


class ExtraInfoWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Minka Extra Info"
    # Short widget description
    description = "Get extra information from Minka observations"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/circle-info-solid-minka.png"
    priority = 4

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False
    
    # We want the current number entered by the user to be saved and restored when saving/loading a workflow. 
    # We can achieve this by declaring a special property/member in the widget’s class definition like so: 
    id_obs = Setting(0)
    #project_name = Setting(None)

    # Widget's outputs; here, a single output named "Number", of type int

    class Inputs:
        data = Input("Data", Orange.data.Table, auto_summary=False)

    class Outputs:
        extra_data = Output("extra", Orange.data.Table, auto_summary=False)


    want_main_area = False

    def __init__(self):
        super().__init__()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, 'No data on input yet, waiting to get something.')
        self.infob = gui.widgetLabel(box, '')

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText(f'{len(dataset)} instances in input dataset')
            df = table_to_frame(dataset)
            ids = df['id'].to_list()
            dic = {}

            progress = gui.ProgressBar(self, len(df))
            
            for id_num in ids:
                url = f'https://minka-sdg.org/observations/{id_num}.json'
                page = requests.get(url, verify=False)

                idents = page.json()['identifications']
                
                if len(idents) > 0:
                    user_identification = idents[0]['user']['login']
                    first_taxon_name = idents[0]['taxon']['name']
                    last_taxon_name = idents[len(idents) - 1]['taxon']['name']
                    dic[id_num] = [user_identification, first_taxon_name, last_taxon_name]
                    progress.advance()
                else:
                    dic[id_num] = [0, 0, 0]
                    progress.advance()
            progress.finish()    

            df['first_identification'] = df['id'].apply(lambda x: str(dic[x][0]))
            df['first_taxon_name'] = df['id'].apply(lambda x: str(dic[x][1]))
            df['last_taxon_name'] = df['id'].apply(lambda x: str(dic[x][2]))

            df['first_taxon_match'] = np.where(df['first_taxon_name'] == df['last_taxon_name'], 'True', 'False')
            df['first_identification_match'] = np.where(df['first_identification'] == df['user_login'], 'True', 'False')
            
            out = table_from_frame(df)
            
            self.infob.setText(f'Observations gathered: {len(df)}')

            self.Outputs.extra_data.send(out)

        else:
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
            #self.Outputs.sample.send("Sampled Data")

if __name__ == "__main__":
    WidgetPreview(ExtraInfoWidget).run()

