import traceback

import Orange.data
import pandas as pd
import requests
from AnyQt.QtGui import QIntValidator
from mecoda_minka import get_dfs, get_obs
from Orange.data.pandas_compat import table_from_frame
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.utils.widgetpreview import WidgetPreview
from orangewidget.widget import Output, OWBaseWidget


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
    resizing_enabled = True

    # We don't want the current number entered by the user to be saved
    # and restored when saving/loading a workflow.
    # We can achieve this by declaring schema_only=True
    id_project = Setting("", schema_only=True)
    user = Setting("", schema_only=True)
    taxon = Setting("", schema_only=True)
    id_place = Setting("", schema_only=True)
    introduced = Setting(False, schema_only=True)
    grade = Setting(False, schema_only=True)
    id_taxon = Setting("", schema_only=True)
    starts_on = Setting("", schema_only=True)
    ends_on = Setting("", schema_only=True)
    created_since = Setting("", schema_only=True)
    created_until = Setting("", schema_only=True)
    num_max = Setting(0, schema_only=True)

    # Widget's outputs
    class Outputs:
        observations = Output("Observations", Orange.data.Table, auto_summary=False)
        photos = Output("Photos", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # Calls the init method of the parent class OWBaseWidget
        super().__init__()

        # info area
        infoBox = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(infoBox, "No observations fetched yet.")
        self.infob = gui.widgetLabel(infoBox, "")

        gui.separator(self.controlArea)

        # filters area
        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")

        self.taxon_line = gui.comboBox(
            self.searchBox,
            self,
            "taxon",
            box=None,
            label="Iconic taxon:",
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
                "Cnidaria",
                "Annelida",
                "Platyhelminthes",
                "Echinodermata",
                "Bryozoa",
                "Porifera",
                "Elasmobranchii",
                "Crustacea",
                "Ctenophora",
            ),
            callback=None,
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=False,
            orientation=1,
        )
        self.taxonid_line = gui.lineEdit(
            self.searchBox,
            self,
            "id_taxon",
            label="Taxon ID:",
            orientation=1,
            controlWidth=150,
        )
        self.project_line = gui.lineEdit(
            self.searchBox,
            self,
            "id_project",
            label="Project ID:",
            orientation=1,
            callback=self.id_project_edit,
            controlWidth=150,
        )
        self.place_line = gui.lineEdit(
            self.searchBox,
            self,
            "id_place",
            label="Place ID:",
            orientation=1,
            controlWidth=150,
        )
        self.introduced_line = gui.checkBox(
            self.searchBox,
            self,
            "introduced",
            label="Non-native species (when place is selected)",
        )
        self.user_line = gui.lineEdit(
            self.searchBox,
            self,
            "user",
            label="User name:",
            orientation=1,
            controlWidth=150,
            callback=self.user_edit,
        )

        self.obsBox = gui.widgetBox(self.searchBox, "Observation date:")
        self.starts_on_line = gui.lineEdit(
            self.obsBox,
            self,
            "starts_on",
            label="Starts on (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )
        self.ends_on_line = gui.lineEdit(
            self.obsBox,
            self,
            "ends_on",
            label="Ends on (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )
        self.creationBox = gui.widgetBox(self.searchBox, "Creation date:")
        self.created_since_line = gui.lineEdit(
            self.creationBox,
            self,
            "created_since",
            label="Since (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )
        self.created_until_line = gui.lineEdit(
            self.creationBox,
            self,
            "created_until",
            label="Until (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )

        gui.separator(self.controlArea)

        self.maxBox = gui.widgetBox(self.controlArea, "", spacing=1)

        self.grade_line = gui.checkBox(
            self.maxBox,
            self,
            "grade",
            label="Research grade only",
        )

        self.max_line = gui.spin(
            self.maxBox,
            self,
            "num_max",
            minv=0,
            maxv=300000,
            step=100,
            label="Max number of results:",
            orientation=1,
        )

        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Request", callback=self.commit)

    def info_searching(self):
        self.infoa.setText("Searching...")
        self.infob.setText("Be patient, this could take a while.")

    def id_project_edit(self):
        if self.id_project != "":
            self.user_line.setDisabled(True)
            self.taxon_line.setDisabled(True)
            self.user = ""
            self.taxon = ""
        else:
            self.user_line.setDisabled(False)
            self.taxon_line.setDisabled(False)

    def user_edit(self):
        if self.user != "":
            self.project_line.setDisabled(True)
            self.id_project = ""
        else:
            self.project_line.setDisabled(False)

    def commit(self):
        self.infoa.setText(f"Searching...")
        self.infob.setText(f"")
        try:
            if self.id_project == "":
                id_project = None
            else:
                id_project = self.id_project

            if self.id_taxon == "":
                id_taxon = None
            else:
                id_taxon = self.id_taxon

            if self.taxon == "":
                taxon = None
            else:
                taxon = self.taxon

            if self.user == "":
                user = None
            else:
                user = self.user

            if self.id_place == "":
                id_place = None
                introduced = None
            else:
                id_place = self.id_place

                if self.introduced is True:
                    introduced = True
                else:
                    introduced = None
            if self.grade is True:
                grade = "research"
            else:
                grade = None

            if self.starts_on == "":
                starts_on = None
            else:
                starts_on = self.starts_on

            if self.ends_on == "":
                ends_on = None
            else:
                ends_on = self.ends_on

            if self.created_since == "":
                created_since = None
            else:
                created_since = self.created_since

            if self.created_until == "":
                created_until = None
            else:
                created_until = self.created_until

            if self.num_max == 0:
                num_max = None
            else:
                num_max = self.num_max

            progress = gui.ProgressBar(self, 2)
            progress.advance()

            observations = get_obs(
                id_project=id_project,
                user=user,
                taxon=taxon,
                place_id=id_place,
                starts_on=starts_on,
                ends_on=ends_on,
                created_d1=created_since,
                created_d2=created_until,
                taxon_id=id_taxon,
                num_max=num_max,
                introduced=introduced,
                grade=grade,
            )

            if len(observations) > 0:
                self.df_obs, self.df_photos = get_dfs(observations)
                self.df_obs["taxon_name"] = self.df_obs["taxon_name"].str.lower()
                self.df_photos["taxon_name"] = self.df_photos["taxon_name"].str.lower()
                self.df_photos["obs_url"] = self.df_photos["id"].apply(
                    lambda x: f"https://minka-sdg.org/observations/{x}"
                )
                # error with pd.NA in conversion to table_from_frame
                self.df_obs["taxon_id"] = self.df_obs["taxon_id"].astype(float)
                self.df_obs["taxon_id"] = self.df_obs["taxon_id"].fillna(0)
                self.df_obs.taxon_name = pd.Categorical(self.df_obs.taxon_name)
                self.df_obs.order = pd.Categorical(self.df_obs.order)
                self.df_obs.family = pd.Categorical(self.df_obs.family)
                self.df_obs.genus = pd.Categorical(self.df_obs.genus)

                self.infoa.setText(f"{len(self.df_obs)} observations gathered")
                self.infob.setText(f"{len(self.df_photos)} photos gathered")

                self.Outputs.observations.send(table_from_frame(self.df_obs))

                table_photos = table_from_frame(self.df_photos)
                for meta in table_photos.domain.metas:
                    if meta.name == "photos_medium_url":
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
