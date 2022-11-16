from orangewidget.widget import OWBaseWidget, Output, Input
from orangewidget.settings import Setting
from Orange.widgets.settings import DomainContextHandler, ContextSetting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame, table_to_frame

from smartcitizen_connector import ScApiDevice, rollup_table

# Fixed stations
class SmartcitizenDataWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Smart Citizen Data"

    # Short widget description
    description = "Get data from environmental devices from the Smart Citizen API"

    # An icon resource file path for this widget
    icon = "icons/smartcitizen.png"

    # Priority in the section MECODA
    priority = 12

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = True

    # Defining settings
    device = Setting("", schema_only=True)
    rollup_number = Setting("10", schema_only=True)
    rollup_text = Setting("m", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Inputs:
        devices = Input("Devices", Orange.data.Table, auto_summary = False)

    class Outputs:
        readings = Output("readings", Orange.data.Table, auto_summary = False)

    metadata = None
    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        # Info banners
        self.infoa = gui.widgetLabel(info, 'No data fetched yet.')

        gui.separator(self.controlArea)

        self.rollupBox = gui.widgetBox(self.controlArea, "")

        self.rollup_number_line = gui.lineEdit(
            self.rollupBox,
            self,
            "rollup_number",
            label="Rollup:",
            orientation=1,
            controlWidth=200,
            callback=self.rollup_check
        )

        self.rollup_text_line = gui.comboBox(
            self.rollupBox,
            self,
            "rollup_text",
            label="Rollup units:",
            items=tuple(rollup_table.keys()),
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=True,
            orientation=1,
        )

        # self.resampleBox = gui.widgetBox(self.controlArea, "")

        # self.resample_line = gui.lineEdit(
        #     self.resampleBox,
        #     self,
        #     "resample",
        #     label="Resample:",
        #     orientation=1,
        #     controlWidth=200,
        #     callback=self.rollup_check
        # )

        # self.clean_line = gui.comboBox(
        #     self.resampleBox,
        #     self,
        #     "rollup_text",
        #     label="Rollup units:",
        #     items=tuple(rollup_table.keys()),
        #     sendSelectedValue=True,
        #     emptyString=False,
        #     editable=False,
        #     contentsLength=None,
        #     searchable=True,
        #     orientation=1,
        # )

        gui.separator(self.controlArea)

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Get data", callback=self.commit)

    @Inputs.devices
    def set_data(self, dataset):

        if dataset is not None:

            self.metadata = table_to_frame(dataset, include_metas = True)

            if (self.metadata.shape[0] > 1):

                self.infoa.setText("Select one device first!")
                return
            else:

                if 'device_id' in self.metadata.columns:
                    col = 'device_id'
                elif 'id' in self.metadata.columns:
                    col = 'id'
                else:
                    self.infoa.setText('Error with input data')
                    return

                self.device = self.metadata[col].values[0]

                name = self.metadata['name'].values[0]
                city = self.metadata['city'].values[0]
                country = self.metadata['country_code'].values[0]
                owner = self.metadata['owner_username'].values[0]

                self.infoa.setText(f"Device: {self.device}"+ \
                    f"\nName: {name}" + \
                    f"\nCity: {city} ({country})" + \
                    f"\nBy: {owner}"
                )

            self.rollup_check()

            # Info banners
            self.inforollup = gui.widgetLabel(self.rollupBox, '')

            gui.separator(self.controlArea)

        else:
            self.device = None
            self.infoa.setText("No data on input yet, waiting to get something.")

    def device_id_edit(self):
        if self.device != "":
            index = self.metadata.loc[self.metadata['id'] == int(self.device)].index.tolist()[0]
            name = self.metadata.loc[index, 'name']
            city = self.metadata.loc[index, 'city']
            country = self.metadata.loc[index, 'country_code']
            owner = self.metadata.loc[index, 'owner_username']

            self.infoa.setText(f"Device: {self.device}"+ \
                f"\nName: {name}" + \
                f"\nCity: {city} ({country})" + \
                f"\nBy: {owner}"
            )

        else:
            self.infoa.setText("Select one device to see it's info")
            self.device = None

    def rollup_check(self):
        if self.rollup_number.isnumeric():
            self.rollup = self.rollup_number + str(self.rollup_text)
        else:
            self.inforollup.setText("Rollup needs to be an integer")
            self.rollup = None

    def commit(self):

        if self.device is not None:

            if (self.metadata.shape[0] > 1):
                self.infoa.setText(f'Select a device first.')
                self.info.set_output_summary(self.info.NoOutput)
                return

            if self.rollup is None:
                self.infoa.setText(f'Input a valid rollup.')
                self.info.set_output_summary(self.info.NoOutput)
                return

            d = ScApiDevice(self.device)
            progress = gui.ProgressBar(self, 4)
            progress.advance()

            data = d.get_device_data(
                        min_date = None,
                        max_date = None,
                        rollup = self.rollup,
                        clean_na = None,
                        resample = True)

            progress.advance()

            if data is not None:
                table = table_from_frame(data)
                progress.advance()
                self.Outputs.readings.send(table)
                progress.advance()
                self.infoa.setText(f'Device {self.device} data  downloaded!')
                self.info.set_output_summary(1)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

            progress.finish()

        else:
            self.infoa.setText(f'Select a device first.')
            self.info.set_output_summary(self.info.NoOutput)

        return

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(SmartcitizenDataWidget).run()
