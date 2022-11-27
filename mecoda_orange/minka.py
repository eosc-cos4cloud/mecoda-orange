from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

import pandas as pd
import traceback
import requests

from mecoda_minka import get_obs, get_dfs

places = [
    "",
    "243: Torrelles de Llobregat",
    "244: BioMARató Catalunya",
    "245: BioMARató Girona",
    "246: BioPrat",
    "247: Area marina de Barcelona",
    "248: BioMARató Barcelona",
    "249: BioMARató Tarragona",
    "250: Vedat de Pesca de Ses Negres",
    "251: Area marina de Badalona",
    "252: Area marina de Sant Adrià del Besòs",
    "253: Piscinas del Forum FECDAS",
    "254: Platja Nova Icària",
    "255: Platja Somorrostro",
    "256: Platja Sant Sebastià",
    "257: Platja Banys del Forum",
    "258: Area Sitges prova",
    "259: Biodiversitat Sitges",
    "260: Isola di Tremiti",
    "261: Platges CEM",
    "263: Atles barcelonès",
    "264: Barcelonès",
    "265: Area marina Sant Feliu",
    "266: Sant Vicenç de Montalt mar",
    "267: Desembocadura del Torrent de Sant Joan",
    "268: Posidonia activa 1",
    "269: Posidonia activa 2",
    "270: Posidonia activa 3",
    "271: Quadricules 200x200 Barcelonés",
    "272: Platja del Castell",
]


def get_places(places):
    first = 273
    for number in range(first, first + 10):
        path = f"https://minka-sdg.org/places/{number}.json"
        try:
            name = requests.get(path).json()["name"]
            places.append(f"{number}: {name}")
        except:
            break
    return places


places = get_places(places)


class MinkaWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Minka Obs."
    # Short widget description
    description = "Get observations from the Minka API"

    # An icon resource file path for this widget
    # (a path relative to the module where this widget is defined)
    icon = "icons/minka-logo.png"
    priority = 1

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False
    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # We don't want the current number entered by the user to be saved
    # and restored when saving/loading a workflow.
    # We can achieve this by declaring schema_only=True
    id_obs = Setting("", schema_only=True)
    id_project = Setting("", schema_only=True)
    query = Setting("", schema_only=True)
    user = Setting("", schema_only=True)
    taxon = Setting("", schema_only=True)
    place_name = Setting("", schema_only=True)
    year = Setting("", schema_only=True)
    starts_on = Setting("", schema_only=True)
    ends_on = Setting("", schema_only=True)
    num_max = Setting(10000, schema_only=True)

    # Widget's outputs
    class Outputs:
        observations = Output(
            "Observations",
            Orange.data.Table,
            auto_summary=False
        )
        photos = Output(
            "Photos",
            Orange.data.Table,
            auto_summary=False
        )

    def __init__(self):
        # Calls the init method of the parent class OWBaseWidget
        super().__init__()

        from AnyQt.QtGui import QIntValidator

        infoBox = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(infoBox, "No observations fetched yet.")
        self.infob = gui.widgetLabel(infoBox, "")

        gui.separator(self.controlArea)

        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")

        self.query_line = gui.lineEdit(
            self.searchBox,
            self,
            "query",
            label="Search by words:",
            orientation=1,
            controlWidth=200,
        )
        self.project_line = gui.lineEdit(
            self.searchBox,
            self,
            "id_project",
            label="Project ID:",
            orientation=1,
            callback=self.id_project_edit,
            controlWidth=200,
        )
        self.user_line = gui.lineEdit(
            self.searchBox,
            self,
            "user",
            label="User name:",
            orientation=1,
            controlWidth=200,
            callback=self.user_edit,
        )
        self.place_line = gui.comboBox(
            self.searchBox,
            self,
            "place_name",
            label="Place:",
            items=places,
            editable=False,
            sendSelectedValue=True,
            orientation=1,
        )
        self.taxon_line = gui.comboBox(
            self.searchBox,
            self,
            "taxon",
            box=None,
            label="Taxon:",
            items=(
                "",
                "Animalia",
                "Actinopterygii",
                "Aves",
                "Reptilia",
                "Amphibia",
                "Mammalia",
                "Arachnida",
                "Insecta",
                "Plantae",
                "Fungi",
                "Protozoa",
                "Mollusca",
                "Chromista",
            ),
            callback=None,
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
            controlWidth=120,
            valueType=int,
            validator=QIntValidator(),
        )
        self.starts_on_line = gui.lineEdit(
            self.searchBox,
            self,
            "starts_on",
            label="Starts on (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )
        self.ends_on_line = gui.lineEdit(
            self.searchBox,
            self,
            "ends_on",
            label="Ends on (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )
        self.id_obs_line = gui.lineEdit(
            self.searchBox,
            self,
            "id_obs",
            label="Id of observation:",
            callback=self.id_obs_edit,
            orientation=1,
            controlWidth=120,
        )

        gui.separator(self.controlArea)

        self.maxBox = gui.widgetBox(self.controlArea, "", spacing=1)

        self.max_line = gui.spin(
            self.maxBox,
            self,
            "num_max",
            minv=0,
            maxv=10000,
            step=100,
            label="Max number of results:",
            orientation=1,
        )

        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Commit", callback=self.commit)

    def info_searching(self):
        self.infoa.setText("Searching...")
        self.infob.setText("Be patient, this could take a while.")

    def id_obs_edit(self):
        if self.id_obs != "":
            self.project_line.setDisabled(True)
            self.query_line.setDisabled(True)
            self.user_line.setDisabled(True)
            self.taxon_line.setDisabled(True)
            self.place_line.setDisabled(True)
            self.year_line.setDisabled(True)
            self.starts_on.setDisabled(True)
            self.ends_on.setDisabled(True)
            self.id_project = ""
            self.query = ""
            self.user = ""
            self.taxon = ""
            self.place_name = ""
            self.year = ""
            self.starts_on = ""
            self.ends_on = ""
            self.num_max = ""
        else:
            self.project_line.setDisabled(False)
            self.query_line.setDisabled(False)
            self.user_line.setDisabled(False)
            self.taxon_line.setDisabled(False)
            self.place_line.setDisabled(False)
            self.year_line.setDisabled(False)
            self.starts_on.setDisabled(False)
            self.ends_on.setDisabled(False)
            self.max_line.setDisabled(False)

    def id_project_edit(self):
        if self.id_project != "":
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
            self.id_project = ""
        else:
            self.id_obs_line.setDisabled(False)
            self.project_line.setDisabled(False)

    def commit(self):
        self.infoa.setText(f"Searching...")
        self.infob.setText(f"")
        try:
            if self.id_obs == "":
                id_obs = None
            else:
                id_obs = int(self.id_obs)

            if self.id_project == "":
                id_project = None
            else:
                id_project = self.id_project

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
                place_id = None
            else:
                place_name = self.place_name
                place_id = place_name.split(":")[0]

            if self.starts_on == "":
                starts_on = None
            else:
                starts_on = self.starts_on

            if self.ends_on == "":
                ends_on = None
            else:
                ends_on = self.ends_on

            progress = gui.ProgressBar(self, 2)
            progress.advance()

            observations = get_obs(
                id_obs=id_obs,
                id_project=id_project,
                query=query,
                user=user,
                taxon=taxon,
                place_id=place_id,
                year=year,
                starts_on=starts_on,
                ends_on=ends_on,
                num_max=self.num_max,
            )

            if len(observations) > 0:
                self.df_obs, self.df_photos = get_dfs(observations)
                self.df_obs["taxon_name"] = self.df_obs["taxon_name"].str.lower()
                self.df_photos["taxon_name"] = self.df_photos["taxon_name"].str.lower(
                )
                # error with pd.NA in conversion to table_from_frame
                self.df_obs["taxon_id"].replace({pd.NA: 0}, inplace=True)
                self.df_obs.taxon_name = pd.Categorical(self.df_obs.taxon_name)
                self.df_obs.order = pd.Categorical(self.df_obs.order)
                self.df_obs.family = pd.Categorical(self.df_obs.family)
                self.df_obs.genus = pd.Categorical(self.df_obs.genus)

                self.infoa.setText(f"{len(self.df_obs)} observations gathered")
                self.infob.setText(f"{len(self.df_photos)} photos gathered")

                self.Outputs.observations.send(table_from_frame(self.df_obs))

                table_photos = table_from_frame(self.df_photos)
                for meta in table_photos.domain.metas:
                    if meta.name == "photos.medium_url":
                        meta.attributes = {"type": "image"}

                self.Outputs.photos.send(table_photos)
                self.info.set_output_summary(len(observations))

            else:
                self.infoa.setText(f"Nothing found.")
                self.infob.setText("")
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f"Nothing found.")
            self.infob.setText("")
        except Exception as error:
            traceback_str = "".join(traceback.format_tb(error.__traceback__))
            self.infoa.setText(f"ERROR: \n{str(error)}\n{traceback_str}")
            self.infob.setText("")

        progress.finish()


if __name__ == "__main__":
    WidgetPreview(MinkaWidget).run()
