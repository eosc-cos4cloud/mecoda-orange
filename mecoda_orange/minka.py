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

places = [
    "",
    "361: ANERIS - Badia Roses ",
    "340: ANERIS - Cadaqués",
    "331: ANERIS - Divers - Platja d'Aro",
    "346: ANERIS - Escullera Port de Barcelona",
    "360: ANERIS - Estartit (Opistobrànquis)",
    "342: ANERIS - Llançà",
    "363: ANERIS - Parc Natural Cap de Creus",
    "358: ANERIS - Parc Subaquàtic del Port de Tarragona",
    "343: ANERIS - Port de Barcelona",
    "341: ANERIS - Port de la Selva",
    "344: ANERIS - Sant Adrià del Besòs",
    "359: ANERIS - Tossa de Mar",
    "338: ANERIS - UNISUB - Estartit",
    "345: ANERIS - Vilanova i la Geltrú",
    "312: Àrea Marina de AMB",
    "251: Area marina de Badalona",
    "247: Area marina de Barcelona",
    "252: Area marina de Sant Adrià del Besòs",
    "265: Area marina Sant Feliu",
    "258: Area Sitges prova",
    "275: Athens city, GR, Greece",
    "263: Atles barcelonès",
    "306: Badalona",
    "301: Badia del Vallès",
    "300: Barberà del Vallès",
    "311: Barcelona",
    "264: Barcelonès",
    "279: Begues",
    "259: Biodiversitat Sitges",
    "248: BioMARató Barcelona",
    "244: BioMARató Catalunya",
    "245: BioMARató Girona",
    "249: BioMARató Tarragona",
    "246: BioPrat",
    "329: BM_Águilas",
    "326: BM_Alcúdia",
    "327: BM_Manacor",
    "330: BM_Mazarrón",
    "334: BM_S'illot",
    "328: BM_St.Feliu de Guíxols",
    "335: BM_St.FeliudeGuíxols2",
    "325: BM-Blanes",
    "336: Bogliasco- BioMARató",
    "289: Castellbisbal",
    "277: Castelldefels",
    "299: Cerdanyola del Vallès",
    "286: Cervelló",
    "287: Corbera de Llobregat",
    "297: Cornellà de Llobregat",
    "276: Costa de Mataró",
    "273: Costa del Garraf",
    "267: Desembocadura del Torrent de Sant Joan",
    "337: Diving Cadaqués - ANERIS",
    "324: Ecotros - EcoNau",
    "313: EIN Santes Creus barranc llacunes",
    "314: EIN Santes Creus sense barranc",
    "293: El Papiol",
    "282: El Prat de Llobregat",
    "274: Escullera Port de Barcelona",
    "310: Esplugues de Llobregat",
    "364: Fundació PLEGADIS",
    "278: Gavà",
    "298: Hospitalet de Llobregat",
    "260: Isola di Tremiti",
    "332: Mare jose-avilez",
    "294: Molins de Rei",
    "303: Montcada i Reixac",
    "307: Montgat",
    "362: North Red Sea - Egipcian",
    "290: Pallejà",
    "285: Palma de Cervelló",
    "253: Piscinas del Forum FECDAS",
    "347: Platges Badalona Nord - AMB",
    "348: Platges Badalona Sud - AMB",
    "355: Platges Barcelona Nord - AMB",
    "356: Platges Barcelona Sud - AMB",
    "349: Platges Castelldefels - AMB",
    "261: Platges CEM",
    "354: Platges de Viladecans - AMB",
    "351: Platges El Prat de Llobregat - AMB",
    "350: Platges Gavà - AMB",
    "357: Platges Montgat - AMB",
    "352: Platges Sant Adrià - AMB",
    "257: Platja Banys del Forum",
    "315: Platja de la Barceloneta",
    "316: Platja de la Mar Bella",
    "317: Platja de la Nova Mar Bella",
    "318: Platja de Llevant",
    "319: Platja de Nova Icaria",
    "320: Platja de Sant Miquel",
    "321: Platja de Sant Sebastià",
    "322: Platja de Somorrostro",
    "323: Platja del Bogatell",
    "272: Platja del Castell",
    "254: Platja Nova Icària",
    "256: Platja Sant Sebastià",
    "255: Platja Somorrostro",
    "268: Posidonia activa 1",
    "269: Posidonia activa 2",
    "270: Posidonia activa 3",
    "353: Praia Angeiras - BIOPOLIS",
    "339: Praia do Molhe - BIOPOLIS",
    "333: Praia Vila Cha bioblitz",
    "271: Quadricules 200x200 Barcelonés",
    "302: Ripollet",
    "305: Sant Adrià del Besòs",
    "288: Sant Andreu de la Barca",
    "283: Sant Boi de Llobregat",
    "280: Sant Climent de Llobregat",
    "292: Sant Cugat del Vallés",
    "295: Sant Feliu de Llobregat",
    "296: Sant Joan Despí",
    "309: Sant Just Desvern",
    "266: Sant Vicenç de Montalt mar",
    "291: Sant Vicenç dels Horts",
    "284: Santa Coloma de Cervelló",
    "304: Santa Coloma de Gramenet",
    "308: Tiana",
    "243: Torrelles de Llobregat",
    "250: Vedat de Pesca de Ses Negres",
    "281: Viladecans",
]


def get_places(places):
    first = 365
    for number in range(first, first + 100):
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
    resizing_enabled = True

    # We don't want the current number entered by the user to be saved
    # and restored when saving/loading a workflow.
    # We can achieve this by declaring schema_only=True
    id_obs = Setting("", schema_only=True)
    id_project = Setting("", schema_only=True)
    query = Setting("", schema_only=True)
    user = Setting("", schema_only=True)
    taxon = Setting("", schema_only=True)
    place_name = Setting("", schema_only=True)
    introduced = Setting(False, schema_only=True)
    year = Setting("", schema_only=True)
    starts_on = Setting("", schema_only=True)
    ends_on = Setting("", schema_only=True)
    created_since = Setting("", schema_only=True)
    created_until = Setting("", schema_only=True)
    num_max = Setting(10000, schema_only=True)

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
        self.introduced_line = gui.checkBox(
            self.searchBox,
            self,
            "introduced",
            label="Non-native species (when place is selected)",
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
        self.starts_on_line = gui.lineEdit(
            self.searchBox,
            self,
            "created_since",
            label="Created since (YYYY-MM-DD):",
            orientation=1,
            controlWidth=120,
        )
        self.ends_on_line = gui.lineEdit(
            self.searchBox,
            self,
            "created_until",
            label="Created until (YYYY-MM-DD):",
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
        gui.button(self.commitBox, self, "Request", callback=self.commit)

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
            self.created_since.setDisabled(True)
            self.created_until.setDisabled(True)
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
            self.created_since.setDisabled(False)
            self.created_until.setDisabled(False)
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

            if self.year == "" or self.year == 0:
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
                introduced = None
            else:
                place_name = self.place_name
                place_id = place_name.split(":")[0]
                if self.introduced is True:
                    introduced = True
                else:
                    introduced = None

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
                created_d1=created_since,
                created_d2=created_until,
                num_max=self.num_max,
                introduced=introduced,
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
