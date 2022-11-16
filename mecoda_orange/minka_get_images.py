from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame
from mecoda_minka import get_obs, get_dfs


class ImagesWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Minka Images"
    # Short widget description
    description = "Get photos from selection of observations. Works with data from Minka API."

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/camera-minka.png"
    priority = 2

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
        photos = Output("photos", Orange.data.Table, auto_summary=False)

    want_main_area = False

    def __init__(self):
        super().__init__()

        # GUI
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, 'No data on input yet, waiting to get something.')
        self.infob = gui.widgetLabel(box, '')

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText(f'{len(dataset)} instances in input dataset')
            df = table_to_frame(dataset)
            obs = []

            progress = gui.ProgressBar(self, len(df))

            for id in df['id'].values:
                obs.extend(get_obs(id_obs=id))
                progress.advance()

            df_obs, df_photos = get_dfs(obs)

            out = table_from_frame(df_photos)

            for meta in out.domain.metas:
                if meta.name == "photos.medium_url":
                    meta.attributes = {"type": "image"}

            self.infob.setText(f'Photos gathered: {len(df_photos)}')

            self.Outputs.photos.send(out)

            progress.finish()

        else:
            self.infoa.setText(
                'No data on input yet, waiting to get something.')
            self.infob.setText('')


if __name__ == "__main__":
    WidgetPreview(ImagesWidget).run()
