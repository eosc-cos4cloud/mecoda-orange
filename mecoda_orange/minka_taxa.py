from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

import pandas as pd
import requests
from mecoda_minka import get_obs, get_dfs

#taxon_tree = pd.read_csv("taxon_tree.csv")
taxon_url = "https://raw.githubusercontent.com/eosc-cos4cloud/mecoda-orange/master/mecoda_orange/data/taxon_tree_with_marines.csv"
taxon_tree = pd.read_csv(taxon_url)


def get_descendants(selected_taxon, taxon_tree):
    id_ = taxon_tree[taxon_tree['taxon_name']
                     == selected_taxon]['taxon_id'].item()
    ancestry = taxon_tree[taxon_tree['taxon_name']
                          == selected_taxon]['ancestry'].item()
    result_df = taxon_tree[taxon_tree['ancestry'] ==
                           f"{ancestry}/{id_}"][['taxon_id', 'taxon_name', 'rank']]
    names = result_df.taxon_name.to_list()
    taxa = ["", ]
    for name in names:
        id_taxa = result_df[result_df['taxon_name'] == name]['taxon_id'].item()
        taxa_url = f"https://minka-sdg.org/taxa/{id_taxa}.json"
        obs_count = requests.get(taxa_url).json()['observations_count']
        if obs_count > 0:
            order = result_df[result_df['taxon_name']
                              == name]['rank'].item().capitalize()
            taxa.append(f"{order} {name}")
    return sorted(taxa)


class TaxonWidget(OWBaseWidget):

    # Widget's name as displayed in the canvas
    name = "Minka Taxon Filter"

    # Short widget description
    description = "Get observations from Minka filtered by taxonomic level."

    # An icon resource file path for this widget
    icon = "icons/arrow-down-wide-short-solid-minka.png"

    # Priority in the section MECODA
    priority = 3

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    kingdom = Setting("", schema_only=True)
    filo = Setting("", schema_only=True)
    class_ = Setting("", schema_only=True)
    order = Setting("", schema_only=True)
    family = Setting("", schema_only=True)
    gender = Setting("", schema_only=True)
    species = Setting("", schema_only=True)
    selected = Setting("", schema_only=True)

    # Widget's outputs; here, a single output named "Observations", of type Table
    class Outputs:
        observations = Output(
            "Observations", Orange.data.Table, auto_summary=False)
        photos = Output("Photos", Orange.data.Table, auto_summary=False)

    def __init__(self):
        # use the init method from the class OWBaseWidget
        super().__init__()

        # info area
        info = gui.widgetBox(self.controlArea, "Info")

        self.infoa = gui.widgetLabel(
            info, '\
            Here you can select taxonomic levels<br>\
            to filter observations from <a href="https://minka-sdg.org">minka-sdg.org</a>.'
        )
        self.infob = gui.widgetLabel(
            info,
            'No observations fetched yet.'
        )

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(
            self.controlArea,
            "Taxa fields",
        )

        self.searchBox.setFixedSize(300, 230)

        self.kingdom_line = gui.comboBox(
            self.searchBox,
            self,
            "kingdom",
            box=None,
            labelWidth=None,
            items=(
                '',
                'Kingdom Animalia',
                'Kingdom Plantae',
                'Kingdom Fungi',
                'Kingdom Protozoa',
                'Kingdom Chromista',
                'Kingdom Bacteria',
            ),
            sendSelectedValue=True,
            emptyString=False,
            editable=False,
            contentsLength=None,
            searchable=True,
            orientation=2,
            callback=self.kingdom_edit
        )

        self.filo_line = gui.comboBox(
            self.searchBox,
            self,
            "filo",
            box=None,
            labelWidth=None,
            items=(),
            orientation=1,
            sendSelectedValue=True,
            searchable=True,
            callback=self.filo_edit
        )

        self.class_line = gui.comboBox(
            self.searchBox,
            self,
            "class_",
            box=None,
            labelWidth=None,
            items=(),
            orientation=1,
            sendSelectedValue=True,
            searchable=True,
            callback=self.class_edit
        )

        self.order_line = gui.comboBox(
            self.searchBox,
            self,
            "order",
            box=None,
            labelWidth=None,
            items=(),
            orientation=1,
            sendSelectedValue=True,
            searchable=True,
            callback=self.order_edit
        )

        self.family_line = gui.comboBox(
            self.searchBox,
            self,
            "family",
            box=None,
            labelWidth=None,
            items=(),
            orientation=1,
            sendSelectedValue=True,
            searchable=True,
            callback=self.family_edit
        )

        self.gender_line = gui.comboBox(
            self.searchBox,
            self,
            "gender",
            box=None,
            labelWidth=None,
            items=(),
            orientation=1,
            sendSelectedValue=True,
            searchable=True,
            callback=self.gender_edit
        )

        self.species_line = gui.comboBox(
            self.searchBox,
            self,
            "species",
            box=None,
            labelWidth=None,
            items=(),
            orientation=1,
            sendSelectedValue=True,
            searchable=True,
        )

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Commit", callback=self.commit)

    def info_searching(self):
        self.infoa.setText('Searching...')

    # function to change subtype items due to type choice
    def kingdom_edit(self):
        self.infoa.setText(f'Selected: {self.kingdom}')
        self.infob.setText('')

        if self.kingdom != "":
            kingdom = self.kingdom.split(" ")[1]
            self.filo_line.clear()
            self.filo_line.addItems(get_descendants(kingdom, taxon_tree))
            self.selected = kingdom

    def filo_edit(self):
        self.infoa.setText(f'Selected: {self.kingdom} \n>> {self.filo}')
        self.infob.setText('')

        if self.filo != "":
            filo = self.filo.split(" ")[1]
            self.class_line.clear()
            self.class_line.addItems(get_descendants(filo, taxon_tree))
            self.selected = filo

    def class_edit(self):
        self.infoa.setText(
            f'Selected: {self.kingdom} \n>> {self.filo} \n>> {self.class_}')
        self.infob.setText('')

        if self.class_ != "":
            class_ = self.class_.split(" ")[1]
            self.order_line.clear()
            self.order_line.addItems(get_descendants(class_, taxon_tree))
            self.selected = class_

    def order_edit(self):
        self.infoa.setText(
            f'Selected: {self.kingdom} \n>> {self.filo} \n>> {self.class_} \n>> {self.order}')
        self.infob.setText('')
        if self.order != "":
            order = self.order.split(" ")[1]
            self.family_line.clear()
            self.family_line.addItems(get_descendants(order, taxon_tree))
            self.selected = order

    def family_edit(self):
        self.infoa.setText(
            f'Selected: {self.kingdom} \n>> {self.filo} \n>> {self.class_} \n>> {self.order} \n>> {self.family}')
        self.infob.setText('')
        if self.family != "":
            family = self.family.split(" ")[1]
            self.gender_line.clear()
            self.gender_line.addItems(get_descendants(family, taxon_tree))
            self.selected = family

    def gender_edit(self):
        self.infoa.setText(
            f'Selected: {self.kingdom} \n>> {self.filo} \n>> {self.class_} \n>> {self.order} \n>> {self.family} \n>> {self.gender}')
        self.infob.setText('')
        if self.gender != "":
            gender = self.gender.split(" ")[1]
            self.species_line.clear()
            self.species_line.addItems(get_descendants(gender, taxon_tree))
            self.selected = gender

    def species_edit(self):
        self.infoa.setText(
            f'Selected: {self.kingdom} \n>> {self.filo} \n>> {self.class_} \n>> {self.order} \n>> {self.family} \n>> {self.gender} \n>> {self.species}')
        self.infob.setText('')
        if self.species != "":
            species = self.species.replace("Species ", "")
            self.selected = species

    def commit(self):
        self.infoa.setText(f'Searching...')
        self.infob.setText(f'')
        try:
            if self.species != "":
                species = self.species.replace("Species ", "")
                self.selected = species
            # show progress bar
            progress = gui.ProgressBar(self, 2)
            progress.advance()
            id_selected = taxon_tree[taxon_tree['taxon_name']
                                     == self.selected].taxon_id.item()

            taxa_url = f"https://minka-sdg.org/taxa/{id_selected}.json"
            obs_count = requests.get(taxa_url).json()['observations_count']

            if obs_count > 0:
                obs = get_obs(taxon_id=id_selected)

                if len(obs) > 0:
                    self.df_obs, self.df_photos = get_dfs(obs)

                    self.df_obs.taxon_name = pd.Categorical(
                        self.df_obs.taxon_name)
                    self.df_obs.order = pd.Categorical(self.df_obs.order)
                    self.df_obs.family = pd.Categorical(self.df_obs.family)
                    self.df_obs.genus = pd.Categorical(self.df_obs.genus)

                    self.df_obs['taxon_name'] = self.df_obs['taxon_name'].str.lower()
                    self.df_photos['taxon_name'] = self.df_photos['taxon_name'].str.lower(
                    )

                    self.infoa.setText(f'{len(obs)} observations gathered')
                    self.infob.setText(
                        f'{len(self.df_photos)} photos gathered'
                    )

                    self.Outputs.observations.send(
                        table_from_frame(self.df_obs))

                    table_photos = table_from_frame(self.df_photos)
                    for meta in table_photos.domain.metas:
                        if meta.name == "photos.medium_url":
                            meta.attributes = {"type": "image"}

                    self.Outputs.photos.send(table_photos)
                    self.info.set_output_summary(len(obs))

                else:
                    self.infoa.setText(f'Nothing found.')
                    self.infob.setText("")
                    self.info.set_output_summary(self.info.NoOutput)

        except ValueError:
            self.infoa.setText(f'Nothing found.')

        except Exception as error:
            self.infoa.setText(f'ERROR: \n{error}')

        progress.finish()


# For developer purpose, allow running the widget directly with python
if __name__ == "__main__":
    WidgetPreview(TaxonWidget).run()
