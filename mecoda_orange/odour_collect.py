
from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame
import pandas as pd
import pyodourcollect.ocmodels as ocmodels
import pyodourcollect.occore as occore
import datetime
from pyodourcollect.ochelpers import TYPE_LIST
from pyodourcollect.ocmodels import GPScoords


def get_type_from_category(choice):
    correspondences = {
        0: [i for i in range(1, 90)],
        1: [i for i in range(1, 10)],
        2: [i for i in range(10, 16)],
        3: [i for i in range(16, 26)],
        4: [i for i in range(26, 44)],
        5: [i for i in range(44, 58)],
        6: [i for i in range(58, 74)],
        7: [i for i in range(74, 88)],
        8: [89],
        9: [88],
    }
    set_items = ['']
    if choice != 0:
        for i in correspondences[choice]:
            set_items.append(TYPE_LIST[i].split("|")[1])
    else:
        for i in correspondences[choice]:
            set_items.append(TYPE_LIST[i].replace("|", " | "))

    return set_items


def get_subtype_from_correspondences(odour_type, odour_subtype):
    correspondences = {
        0: [i for i in range(1, 90)],
        1: [i for i in range(1, 10)],
        2: [i for i in range(10, 16)],
        3: [i for i in range(16, 26)],
        4: [i for i in range(26, 44)],
        5: [i for i in range(44, 58)],
        6: [i for i in range(58, 74)],
        7: [i for i in range(74, 88)],
        8: [89],
        9: [88],
    }
    subtype = correspondences[odour_type][odour_subtype]
    return subtype


class OdourCollectWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "OdourCollect Obs."

    # Short widget description
    description = "Get observations from Odour Collect API"

    # An icon resource file path for this widget
    icon = "icons/odourcollect-logo.png"

    # Priority in the section MECODA
    priority = 6

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    date_init = Setting("2019-01-01", schema_only=True)
    date_end = Setting(str(datetime.date.today()), schema_only=True)
    minAnnoy = Setting(-4, schema_only=True)
    maxAnnoy = Setting(4, schema_only=True)
    minIntensity = Setting(0, schema_only=True)
    maxIntensity = Setting(6, schema_only=True)
    type = Setting(0, schema_only=True)
    subtype = Setting(0, schema_only=True)
    poi_coords_lat = Setting("", schema_only=True)
    poi_coords_lon = Setting("", schema_only=True)

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

        # searchBox area
        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")

        self.date_init_line = gui.lineEdit(
            self.searchBox,
            self,
            "date_init",
            label="Initial Date:",
            orientation=1,
            controlWidth=140,
        )

        self.date_end_line = gui.lineEdit(
            self.searchBox,
            self,
            "date_end",
            label="End Date:",
            orientation=1,
            controlWidth=140
        )

        gui.separator(self.searchBox)

        self.minAnnoy_line = gui.hSlider(
            self.searchBox,
            self,
            "minAnnoy",
            minValue=-4,
            maxValue=4,
            step=1,
            label="Min. Annoy:",
            vertical=False
        )

        self.maxAnnoy_line = gui.hSlider(
            self.searchBox,
            self,
            "maxAnnoy",
            minValue=-4,
            maxValue=4,
            step=1,
            label="Max. Annoy:",
            vertical=False
        )

        gui.separator(self.searchBox)

        self.minIntensity_line = gui.hSlider(
            self.searchBox,
            self,
            "minIntensity",
            minValue=0,
            maxValue=6,
            step=1,
            label="Min. Intensity:",
            vertical=False
        )

        self.maxIntensity_line = gui.hSlider(
            self.searchBox,
            self,
            "maxIntensity",
            minValue=0,
            maxValue=6,
            step=1,
            label="Max. Intensity:",
            vertical=False
        )

        gui.separator(self.searchBox)

        self.type_line = gui.comboBox(
            self.searchBox,
            self,
            "type",
            box=None,
            label="Category:",
            labelWidth=None,
            items=(
                '',
                'Waste related odours',
                'Waste water related odours',
                'Agriculture and livestock related odours',
                'Food Industries related odours',
                'Industry related odours',
                'Urban odours',
                'Nice odours',
                'Other odours not fitting elsewhere',
                'No odour observations',
            ),
            sendSelectedValue=False,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=True,
            orientation=1,
            callback=self.type_edit
        )

        self.subtype_line = gui.comboBox(
            self.searchBox,
            self,
            "subtype",
            box=None,
            label="Type:",
            labelWidth=None,
            items=get_type_from_category(self.type),
            orientation=1,
            sendSelectedValue=False,
            searchable=True,
        )

        # poi area
        self.poi = gui.widgetBox(
            self.controlArea, "Point of Interest", spacing=2)
        self.poi_lat_line = gui.lineEdit(
            self.poi,
            self,
            "poi_coords_lat",
            label="Latitude:",
            orientation=0,
            controlWidth=140,
            valueType=float
        )

        self.poi_lon_line = gui.lineEdit(
            self.poi,
            self,
            "poi_coords_lon",
            label="Longitude:",
            orientation=0,
            controlWidth=140,
            valueType=float
        )

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Commit", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')

    # function to change subtype items due to type choice
    def type_edit(self):
        self.subtype_line.clear()
        if self.type in range(1, 10):
            self.subtype_line.addItems(get_type_from_category(self.type))

        elif (self.type == "") or (self.type == 0):
            self.subtype_line.addItems(get_type_from_category(0))

    def commit(self):
        self.infoa.setText(f'Searching...')
        self.infob.setText(f'')
        try:
            # convert date_init and date_end to datetime format
            if type(self.date_init) == str:
                init = datetime.datetime.strptime(
                    self.date_init, '%Y-%m-%d').date()
            else:
                init = self.date_init

            if type(self.date_end) == str:
                end = datetime.datetime.strptime(
                    self.date_end, '%Y-%m-%d').date()
            else:
                end = self.date_end

            # convert subtype to number 0-89
            if self.subtype != 0:
                subtype = get_subtype_from_correspondences(
                    self.type, self.subtype)
            else:
                subtype = 0

            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()

            requestparams = ocmodels.OCRequest(
                date_init=init,
                date_end=end,
                minAnnoy=self.minAnnoy,
                maxAnnoy=self.maxAnnoy,
                minIntensity=self.minIntensity,
                maxIntensity=self.maxIntensity,
                type=self.type,
                subtype=subtype
            )

            # construct GPScoords
            if (self.poi_coords_lat != "") and (self.poi_coords_lon != ""):
                poi_coords = GPScoords(
                    lat=float(self.poi_coords_lat), long=float(self.poi_coords_lon))
            else:
                poi_coords = None

            observations = occore.get_oc_data(requestparams, poi_coords)

            # convert lon-lat and create columns from time
            observations[['longitude', 'latitude']] = observations[[
                'longitude', 'latitude']].astype(float)
            observations[['time_hour', 'time_min', 'time_sec']] = observations.time.astype(
                str).str.split(":", expand=True)

            if len(observations) > 0:

                table_oc = table_from_frame(observations)

                self.infoa.setText(
                    f'{len(observations)} observations gathered')
                self.info.set_output_summary(len(observations))

                self.Outputs.observations.send(table_oc)

            else:
                self.infoa.setText(f'Nothing found.')
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')

        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')

        progress.finish()


# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(OdourCollectWidget).run()
