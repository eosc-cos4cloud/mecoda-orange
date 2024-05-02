from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

from smartcitizen_connector import SCDevice, search_by_query
from smartcitizen_connector.tools import dict_unpack
from pandas import DataFrame

unhashable_columns = ['notify', 'data', 'owner', 'kit', 'location', 'hardware_info', 'postprocessing', 'device_token', 'hardware']

# Fixed stations
class SmartcitizenSearchWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Smart Citizen Search"

    # Short widget description
    description = "Search environmental devices from the Smart Citizen API"

    # An icon resource file path for this widget
    icon = "icons/smartcitizen_search.png"

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
            # self.kit_id_line.setDisabled(True)
            self.city_line.setDisabled(True)
            self.tags_line.setDisabled(True)
            self.user_line.setDisabled(True)

            # self.kit_id = ""
            self.city = ""
            self.tags = ""
            self.user = ""

        else:
            # self.kit_id_line.setDisabled(False)
            self.city_line.setDisabled(False)
            self.tags_line.setDisabled(False)
            self.user_line.setDisabled(False)

    def tags_edit(self):
        if "," in self.tags:
            t = self.tags.split(",")
            self.tags_tokenized = [x.strip() for x in t]
        else:
            if self.tags:
                self.tags_tokenized = [self.tags]
            else:
                self.tags_tokenized = None

    def commit(self):
        progress = gui.ProgressBar(self, 3)
        progress.advance()

        if self.device_id != "":

            if self.user != "" or self.city != "":
                self.infoa.setText(f'Ignoring search filters')
            self.infoa.setText(f'Collecting device...')

            d = SCDevice(self.device_id)

            if d is not None:
                df = DataFrame(list(d.json.model_dump().items())).set_index(0).T.set_index('id')

                df['owner_id'] = df.loc[int(self.device_id), 'owner']['id']
                df['owner_username'] = df.loc[int(self.device_id), 'owner']['username']
                df['latitude'] = df.loc[int(self.device_id), 'location']['latitude']
                df['longitude'] = df.loc[int(self.device_id), 'location']['longitude']
                df['city'] = df.loc[int(self.device_id), 'location']['city']
                df['country_code'] = df.loc[int(self.device_id), 'location']['country_code']
                df['device_id'] = int(self.device_id)

                df['system_tags'] = df['system_tags'].astype('str')
                df['user_tags'] = df['user_tags'].astype('str')

                df.drop(columns = unhashable_columns, errors='ignore', inplace=True)
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
            if self.city == "": city = None
            else: city = self.city

            self.infoa.setText(f'Looking for devices...')
            self.infoa.setText(f'')

            # Query list for different devices
            query_list = []
            if owner_username is not None:
                query_list.append({
                        'key': 'owner_username',
                        'value': owner_username,
                        'search_matcher': 'eq'
                    })

            if city is not None:
                    query_list.append({
                        'key': 'tags_name',
                        'value': city,
                        'search_matcher': 'in'
                    })

            if self.tags_tokenized is not None:
                    query_list.append({
                        'key': 'tags_name',
                        'value': self.tags_tokenized,
                        'search_matcher': 'in'
                    } )

            if len(query_list):
                devices = search_by_query(
                    endpoint= 'devices',
                    search_items= query_list)
            else:
                self.infoa.setText(f'At least one field is required.')
                self.info.set_output_summary(self.info.NoOutput)
                progress.finish()
                return

            if devices is None:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)
                progress.finish()
                return

            if len(devices):
                devices['owner_id'] = devices.apply(dict_unpack, column='owner', key='id', axis=1)
                devices['owner_username'] = devices.apply(dict_unpack, column='owner', key='username', axis=1)
                devices['latitude'] = devices.apply(dict_unpack, column='location', key='latitude', axis=1)
                devices['longitude'] = devices.apply(dict_unpack, column='location', key='longitude', axis=1)
                devices['city'] = devices.apply(dict_unpack, column='location', key='city', axis=1)
                devices['country_code'] = devices.apply(dict_unpack, column='location', key='country_code', axis=1)

                devices['system_tags'] = devices['system_tags'].astype('str')
                devices['user_tags'] = devices['user_tags'].astype('str')

                devices.drop(columns = unhashable_columns, errors='ignore', inplace=True)

                table = table_from_frame(devices)
                progress.advance()
                self.infoa.setText(f'{len(devices)} devices gathered')
                self.info.set_output_summary(len(devices))
                self.Outputs.deviceTable.send(table)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)
                progress.finish()
                return

        progress.finish()

# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(SmartcitizenSearchWidget).run()
