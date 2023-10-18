import io
import shutil
import zipfile

import Orange.data
import pandas as pd
import requests
from Orange.data.pandas_compat import table_from_frame, table_to_frame
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.utils.widgetpreview import WidgetPreview
from orangewidget.widget import Output, OWBaseWidget


class PlantnetWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Plantnet"

    # Short widget description
    description = "Get identification from Plantnet"

    # An icon resource file path for this widget
    icon = "icons/plantnet.png"

    # Priority in the section MECODA
    priority = 8

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    organ = Setting("", schema_only=True)
    photo_url = Setting("", schema_only=True)

    # Widget's inputs and outputs
    class Outputs:
        results = Output("results", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()
        self.dataset = None

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(info, "Pl@ntNet API request")
        self.infob = gui.widgetLabel(
            info, "<br>Press SEND to get data from this image."
        )

        gui.separator(self.controlArea)

        # filters area
        self.searchBox = gui.widgetBox(self.controlArea, "Search fields")
        self.query_line = gui.lineEdit(
            self.searchBox,
            self,
            "photo_url",
            label="URL to image:",
            orientation=1,
            controlWidth=300,
        )
        self.taxon_line = gui.comboBox(
            self.searchBox,
            self,
            "organ",
            box=None,
            label="Organ:",
            items=(
                "auto",
                "leaf",
                "flower",
                "fruit",
                "bark",
            ),
            callback=None,
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=False,
            orientation=1,
        )
        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Send", callback=self.commit)

    def info_searching(self):
        self.infoa.setText("Searching...")

    def commit(self):
        self.infoa.setText(f"Loading...")
        self.infob.setText(f"This could take a while.")

        try:
            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()

            # se indica url de la foto
            if self.photo_url != "":
                # print(type(self.photo_url), self.photo_url)
                image_path = (
                    self.photo_url.replace("/medium/", "/original/")
                    .replace(":", "%3A")
                    .replace("/", "%2F")
                    .replace("?", "%3F")
                )
                url = f"https://my-api.plantnet.org/v2/identify/all?images={image_path}&organs={self.organ}&include-related-images=false&no-reject=false&lang=en&api-key=2b10xMRqm3L3dcygRLsRrFapjO"
                req = requests.get(url).json()
                # sacamos scores
                scores = []
                for i in range(len(req["results"])):
                    datos = {}
                    datos["sci_name"] = req["results"][i]["species"][
                        "scientificNameWithoutAuthor"
                    ]
                    datos["genus"] = req["results"][i]["species"]["genus"][
                        "scientificNameWithoutAuthor"
                    ]
                    datos["family"] = req["results"][i]["species"]["family"][
                        "scientificNameWithoutAuthor"
                    ]
                    datos["species_score"] = round(
                        (req["results"][i]["score"]) * 100, 2
                    )
                    scores.append(datos)
                result_df = pd.DataFrame(scores)
                self.Outputs.results.send(table_from_frame(result_df))
                self.infoa.setText(f'<b>{result_df["sci_name"].head(1).item()}</b>')
                self.infob.setText(
                    f'Probability: {result_df["species_score"].head(1).item()}%'
                )

            else:
                self.infoa.setText(f"Nothing found.")
                self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f"Nothing found.")

        except Exception as error:
            self.infoa.setText(f"ERROR: \n{error}")

        progress.finish()


# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(PlantnetWidget).run()
