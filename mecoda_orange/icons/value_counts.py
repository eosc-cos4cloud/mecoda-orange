from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
from mecoda_nat import get_obs, get_dfs


class ObservationsWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Value Count"
    # Short widget description
    description = "Count number of appearances in a column of Table"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/calculator-solid.svg"
    priority = 3

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
        value_counts = Output("value_counts", Orange.data.Table, auto_summary=False)


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
            self.infoa.setText('%d instances in input dataset' % len(dataset))
            df = table_to_frame(dataset)
            df_count = df.value_counts(dropna=False)
            df_count.name = "Number"
            count = table_from_frame(df_count)

            self.infob.setText(f'Value count for column: {dataset.domain[0]}')
            self.Outputs.value_counts.send(count)
        else:
            self.infoa.setText('No data on input yet, waiting to get something.')
            self.infob.setText('')
            #self.Outputs.sample.send("Sampled Data")

if __name__ == "__main__":
    WidgetPreview(ObservationsWidget).run()

