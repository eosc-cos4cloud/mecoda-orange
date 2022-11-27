from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame
from mecoda_nat import get_obs, get_dfs
from typing import Optional, List
import pandas as pd


class NatusferaWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Natusfera Obs."
    # Short widget description
    description = "Get observations from the Natusfera API"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    #icon = "icons/N2.png"
    icon = "icons/natusfera_v1.png"
    priority = 8

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = True

    # We want the current number entered by the user to be saved and restored when saving/loading a workflow.
    # We can achieve this by declaring a special property/member in the widget’s class definition like so:
    id_obs = Setting("", schema_only=True)
    project_name = Setting("", schema_only=True)
    query = Setting("", schema_only=True)
    user = Setting("", schema_only=True)
    taxon = Setting("", schema_only=True)
    place_name = Setting("", schema_only=True)
    year = Setting("", schema_only=True)
    num_max = Setting(20000, schema_only=True)

    # Widget's outputs; here, a single output named "Number", of type int
    class Outputs:
        observations = Output(
            "Observations", Orange.data.Table, auto_summary=False)
        photos = Output("Photos", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # llama el método init de la clase padre OWBaseWidget
        super().__init__()

        from AnyQt.QtGui import QIntValidator

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, 'No observations fetched yet.')
        self.infob = gui.widgetLabel(box, '')

        gui.separator(self.controlArea)

        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")

        # gui.spin(self.searchBox, self, 'id_obs',
        #         minv=0, maxv=400000, step=1, label='Enter an id of observation:')
        self.query_line = gui.lineEdit(
            self.searchBox, self, "query", label="Search by words:", orientation=1, controlWidth=140)
        self.project_line = gui.lineEdit(self.searchBox, self, 'project_name', label="Project name:",
                                         orientation=1, callback=self.project_name_edit, controlWidth=140)
        self.user_line = gui.lineEdit(self.searchBox, self, "user", label="User name:",
                                      orientation=1, controlWidth=140, callback=self.user_edit)
        self.place_line = gui.lineEdit(
            self.searchBox, self, "place_name", label="Place:", orientation=1, controlWidth=140)
        self.taxon_line = gui.comboBox(
            self.searchBox,
            self,
            "taxon",
            box=None,
            label="Taxon:",
            labelWidth=None,
            items=('', 'Animalia', 'Actinopterygii', 'Aves', 'Reptilia', 'Amphibia', 'Mammalia', 'Arachnida', 'Insecta', 'Plantae', 'Fungi', 'Protozoa', 'Mollusca', 'Chromista'), callback=None,
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=False,
            orientation=1,
        )
        self.year_line = gui.lineEdit(
            self.searchBox,
            self,
            "year",
            label="Year:",
            orientation=1,
            controlWidth=80,
            valueType=int,
            validator=QIntValidator()
        )
        self.id_obs_line = gui.lineEdit(self.searchBox, self, 'id_obs', label="Id of observation:",
                                        callback=self.id_obs_edit, orientation=1, controlWidth=80)

        # self.project_line.setDisabled(True)

        #gui.hSlider(self.searchBox, self, "year", box=None, minValue=2000, maxValue=2021, step=1, label="Year", labelFormat=' %d', ticks=False, divideFactor=1.0, vertical=False, createLabel=True)
        gui.separator(self.controlArea)

        self.maxBox = gui.widgetBox(self.controlArea, "", spacing=1)
        #self.max_line = gui.lineEdit(self.maxBox, self, "num_max", label="", orientation=1)
        self.max_line = gui.spin(
            self.maxBox,
            self,
            "num_max",
            minv=0,
            maxv=20000,
            step=200,
            label='Max number of results:',
            orientation=1)

        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Commit", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')

    def id_obs_edit(self):
        if self.id_obs != "":
            self.project_line.setDisabled(True)
            self.query_line.setDisabled(True)
            self.user_line.setDisabled(True)
            self.taxon_line.setDisabled(True)
            self.place_line.setDisabled(True)
            self.year_line.setDisabled(True)
            # self.max_line.setDisabled(True)
            self.project_name = ""
            self.query = ""
            self.user = ""
            self.taxon = ""
            self.place_name = ""
            self.year = ""
            self.num_max = ""
        else:
            self.project_line.setDisabled(False)
            self.query_line.setDisabled(False)
            self.user_line.setDisabled(False)
            self.taxon_line.setDisabled(False)
            self.place_line.setDisabled(False)
            self.year_line.setDisabled(False)
            self.max_line.setDisabled(False)

    def project_name_edit(self):
        if self.project_name != "":
            self.user_line.setDisabled(True)
            self.id_obs_line.setDisabled(True)
            self.taxon_line.setDisabled(True)
            self.user = ""
            self.id_obs = ""
            self.taxon = ""
        else:
            self.user_line.setDisabled(False)
            self.id_obs_line.setDisabled(False)
            self.taxon_line.setDisabled(False)

    def user_edit(self):
        if self.user != "":
            self.id_obs_line.setDisabled(True)
            self.project_line.setDisabled(True)
            self.id_obs = ""
            self.project_name = ""
        else:
            self.id_obs_line.setDisabled(False)
            self.project_line.setDisabled(False)

    def commit(self):
        self.infoa.setText(f'Searching...')
        self.infob.setText(f'')
        try:
            if self.id_obs == "":
                id_obs = None
            else:
                id_obs = int(self.id_obs)

            if self.project_name == "":
                project_name = None
            else:
                project_name = self.project_name

            if self.taxon == "":
                taxon = None
            else:
                taxon = self.taxon

            if self.year == "":
                year = None
            else:
                year = int(self.year)

            if self.query == "":
                query = None
            else:
                query = self.query

            if self.user == "":
                user = None
            else:
                user = self.user

            if self.place_name == "":
                place_name = None
            else:
                place_name = self.place_name

            progress = gui.ProgressBar(self, 2)
            progress.advance()

            observations = get_obs(
                id_obs=id_obs,
                project_name=project_name,
                query=query,
                user=user,
                taxon=taxon,
                place_name=place_name,
                year=year,
                num_max=self.num_max,
            )

            if len(observations) > 0:
                self.df_obs, self.df_photos = get_dfs(observations)
                self.df_obs['taxon_name'] = self.df_obs['taxon_name'].str.lower()
                self.df_photos['taxon_name'] = self.df_photos['taxon_name'].str.lower(
                )

                self.infoa.setText(
                    f'{len(observations)} observations gathered')
                self.infob.setText(f'{len(self.df_photos)} photos gathered')

                self.Outputs.observations.send(table_from_frame(self.df_obs))

                table_photos = table_from_frame(self.df_photos)
                for meta in table_photos.domain.metas:
                    if meta.name == "photos.medium_url":
                        meta.attributes = {"type": "image"}

                self.Outputs.photos.send(table_photos)
                self.info.set_output_summary(len(observations))

            else:
                self.infoa.setText(f'Nothing found.')
                self.infob.setText("")
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')
            self.infob.setText("")
        except Exception as error:
            self.infoa.setText(f'ERROR: \n{str(error)}')
            self.infob.setText("")

        progress.finish()


if __name__ == "__main__":
    WidgetPreview(NatusferaWidget).run()
