from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

from smartcitizen_connector import ScApiDevice
from pandas import DataFrame

# Fixed stations
class SmartcitizenSearchWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Smart Citizen Search"

    # Short widget description
    description = "Search environmental devices from the Smart Citizen API"

    # An icon resource file path for this widget
    icon = "icons/smartcitizen.png"

    # Priority in the section MECODA
    priority = 13

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = True

    # Defining settings
    city = Setting("", schema_only=True)
    user = Setting("", schema_only=True)
    tags = Setting("", schema_only=True)
    device_id = Setting("", schema_only=True)
    kit_id = Setting("", schema_only=True)

    blueprints = ScApiDevice.get_kits()
    # descriptive_blueprints = ('',) + tuple(blueprints['item_descr'].values,)
    descriptive_blueprints = blueprints = ('', ) + tuple(sorted("{0:0=2d}".format(kit.id) + ': ' + kit.name for kit in blueprints),)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        deviceTable = Output("Devices", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        # Info banners
        self.infoa = gui.widgetLabel(info, 'No data fetched yet.')
        self.tags_tokenized = None

        gui.separator(self.controlArea)

        self.searchBox = gui.widgetBox(self.controlArea, "Search filters")
        self.city_line = gui.lineEdit(
            self.searchBox,
            self,
            "city",
            label="City:",
            orientation=1,
            # callback=self.device_id_disable,
            controlWidth=200
            )
        self.tags_line = gui.lineEdit(
            self.searchBox,
            self,
            'tags',
            label="Tags (comma separated):",
            orientation=1,
            callback=self.tags_edit,
            controlWidth=200
            )
        self.user_line = gui.lineEdit(
            self.searchBox,
            self,
            "user",
            label="User name:",
            orientation=1,
            controlWidth=200,
            # callback=self.device_id_disable,
            )

        self.kit_id_line = gui.comboBox(
            self.searchBox,
            self,
            "kit_id",
            box=None,
            label="Kit ID:",
            # labelWidth=None,
            items=self.descriptive_blueprints,
            # callback=self.kit_id_edit,
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=True,
            orientation=1,
            )

        gui.separator(self.controlArea)

        self.deviceBox = gui.widgetBox(self.controlArea, "Or directly find device")
        self.device_id_line = gui.lineEdit(
            self.deviceBox,
            self,
            'device_id',
            label="Device ID:",
            # callback=self.device_id_edit,
            orientation=1,
            controlWidth=120
        )

        gui.separator(self.controlArea)

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Search devices", callback=self.commit)

    def device_id_edit(self):
        if self.device_id_line != "":
            self.kit_id_line.setDisabled(True)
            self.city_line.setDisabled(True)
            self.tags_line.setDisabled(True)
            self.user_line.setDisabled(True)

            self.kit_id = ""
            self.city = ""
            self.tags = ""
            self.user = ""

        else:
            self.kit_id_line.setDisabled(False)
            self.city_line.setDisabled(False)
            self.tags_line.setDisabled(False)
            self.user_line.setDisabled(False)

    def tags_edit(self):
        if "," in self.tags:
            t = self.tags.split(",")
            self.tags_tokenized = [x.strip() for x in t]
        else:
            self.tags_tokenized = [self.tags]

    def commit(self):
        progress = gui.ProgressBar(self, 3)
        progress.advance()

        if self.device_id != "":

            if self.user != "" or self.kit_id != "" or self.city != "":
                self.infoa.setText(f'Ignoring search filters')
            self.infoa.setText(f'Collecting device...')

            d = ScApiDevice.get_device_info(self.device_id)

            if d is not None:
                df = DataFrame(list(d.dict().items())).set_index(0).T.set_index('id')
                df['kit_id'] = df['kit_id'].astype('int')
                df['owner_id'] = df['owner_id'].astype('float')
                df['latitude'] = df['latitude'].astype('float')
                df['longitude'] = df['longitude'].astype('float')
                df['device_id'] = int(self.device_id)

                df['system_tags'] = df['system_tags'].astype('str')
                df['user_tags'] = df['user_tags'].astype('str')

                table = table_from_frame(df)

                progress.advance()
                self.Outputs.deviceTable.send(table)
                self.infoa.setText(f'Device {self.device_id} gathered')
                self.info.set_output_summary(1)

            else:
                self.infoa.setText(f'Device {self.device_id} not found. Check again')
                self.info.set_output_summary(self.info.NoOutput)

        else:

            if self.user == "": owner_username = None
            else: owner_username = self.user
            if self.kit_id == "": kit_id = None
            else: kit_id = int(self.kit_id.split(':')[0])
            if self.city == "": city = None
            else: city = self.city

            self.infoa.setText(f'Looking for devices...')
            self.infoa.setText(f'')

            devices = ScApiDevice.get_devices(
                owner_username=owner_username,
                kit_id = kit_id,
                city = city,
                tags = self.tags_tokenized,
                full = True)

            if len(devices) > 0:
                df = DataFrame([device.__dict__ for device in devices])

                df['system_tags'] = df['system_tags'].astype('str')
                df['user_tags'] = df['user_tags'].astype('str')

                table = table_from_frame(df)
                progress.advance()
                self.infoa.setText(f'{len(devices)} devices gathered')
                self.info.set_output_summary(len(devices))
                self.Outputs.deviceTable.send(table)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

        # except ValueError:
        #     self.infoa.setText(f'Nothing found.')

        # except Exception as error:
        #     self.infoa.setText(f'ERROR: \n{error}')

        progress.finish()

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(SmartcitizenSearchWidget).run()
