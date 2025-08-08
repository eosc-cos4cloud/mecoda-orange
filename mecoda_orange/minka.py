import traceback

import Orange.data
import pandas as pd
import requests
from mecoda_minka import get_dfs, get_obs
from Orange.data.pandas_compat import table_from_frame
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.utils.widgetpreview import WidgetPreview
from orangewidget.widget import Output, OWBaseWidget

session = requests.Session()


def _get_id_from_name(taxon_name, session):
    taxon_name = taxon_name.replace(" ", "%20")
    taxon_name = taxon_name.capitalize()
    url = f"https://minka-sdg.org/taxon_names.json?name={taxon_name}"
    try:
        taxon_id = session.get(url).json()[0]["taxon_id"]
    except IndexError:
        taxon_id = 0
    return taxon_id


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
    url_project = Setting("", schema_only=True)
    user = Setting("", schema_only=True)
    taxon = Setting("", schema_only=True)
    url_place = Setting("", schema_only=True)
    introduced = Setting(False, schema_only=True)
    grade = Setting(False, schema_only=True)
    taxon_name = Setting("", schema_only=True)
    starts_on = Setting("", schema_only=True)
    ends_on = Setting("", schema_only=True)
    created_since = Setting("", schema_only=True)
    created_until = Setting("", schema_only=True)
    num_max = Setting(0, schema_only=True)

    # Widget's outputs
    class Outputs:
        observations = Output("Observations", Orange.data.Table, auto_summary=False)
        photos = Output("Photos", Orange.data.Table, auto_summary=False)
        users = Output("Users", Orange.data.Table, auto_summary=False)

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
            "taxon_name",
            label="Taxon Name:",
            orientation=1,
            controlWidth=200,
        )
        self.project_line = gui.lineEdit(
            self.searchBox,
            self,
            "url_project",
            label="Project URL:",
            orientation=1,
            # callback=self.id_project_edit,
            controlWidth=200,
        )
        self.place_line = gui.lineEdit(
            self.searchBox,
            self,
            "url_place",
            label="Place URL:",
            orientation=1,
            controlWidth=200,
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
            # callback=self.user_edit,
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

    def commit(self):
        self.infoa.setText(f"Searching...")
        self.infob.setText(f"Be patient, this could take a while.")
        progress = gui.ProgressBar(self, 3)
        
        try:
            if self.url_project == "":
                id_project = None
            else:
                id_project = session.get(f"{self.url_project}.json").json()["id"]

            if self.taxon_name == "":
                id_taxon = None
            else:
                id_taxon = _get_id_from_name(self.taxon_name, session)
                if id_taxon == 0:
                    self.infoa.setText(f"Invalid taxon name.")
                    self.infob.setText("")
                    return

            if self.taxon == "":
                taxon = None
            else:
                taxon = self.taxon

            if self.user == "":
                user = None
            else:
                user = self.user

            if self.url_place == "":
                id_place = None
                introduced = None
            else:
                id_place = session.get(f"{self.url_place}.json").json()["id"]

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

            progress.advance()
            print(num_max)
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
                self.infoa.setText(f"Processing {len(observations)} observations...")
                progress.advance()
                self.df_obs, self.df_photos = get_dfs(observations)
                # Optimize string operations with vectorized approach
                if not self.df_obs.empty:
                    self.df_obs["taxon_name"] = self.df_obs["taxon_name"].str.lower()
                if not self.df_photos.empty:
                    self.df_photos["taxon_name"] = self.df_photos["taxon_name"].str.lower()
                # Vectorized URL generation (much faster than apply)
                self.df_photos["obs_url"] = "https://minka-sdg.org/observations/" + self.df_photos["id"].astype(str)
                # Optimize data type conversions
                self.df_obs["taxon_id"] = pd.to_numeric(self.df_obs["taxon_id"], errors='coerce').fillna(0)
                
                # Batch convert to categorical (more efficient)
                categorical_cols = ["user_login", "taxon_name", "order", "family", "genus"]
                for col in categorical_cols:
                    if col in self.df_obs.columns:
                        self.df_obs[col] = pd.Categorical(self.df_obs[col])

                self.infoa.setText(f"{len(self.df_obs)} observations gathered")
                self.infob.setText(f"{len(self.df_photos)} photos gathered")

                self.Outputs.observations.send(table_from_frame(self.df_obs))

                table_photos = table_from_frame(self.df_photos)
                for meta in table_photos.domain.metas:
                    if meta.name == "photos_medium_url":
                        meta.attributes = {"type": "image"}

                self.Outputs.photos.send(table_photos)

                # Optimize users table processing
                unique_observers = self.df_obs.user_login.unique().tolist()
                
                # More efficient identifier processing
                identifiers_series = self.df_obs["identifiers"].dropna()
                if not identifiers_series.empty:
                    all_identifiers_flat = identifiers_series.str.split(", ").explode()
                    unique_identifiers = all_identifiers_flat.dropna().unique().tolist()
                    # Clean up temporary data
                    del all_identifiers_flat
                else:
                    unique_identifiers = []
                
                total_observers = list(set(unique_identifiers + unique_observers))
                # Clean up temporary data
                del identifiers_series

                df_users = pd.DataFrame(
                    {
                        "field": ["observers", "identifiers", "total_participants"],
                        "list_users": [
                            ", ".join(unique_observers),
                            ", ".join(unique_identifiers),
                            ", ".join(total_observers),
                        ],
                        "num_users": [
                            len(unique_observers),
                            len(unique_identifiers),
                            len(total_observers),
                        ],
                    }
                )
                self.Outputs.users.send(table_from_frame(df_users))

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
