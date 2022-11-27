from orangewidget.widget import OWBaseWidget, Output
from orangewidget.settings import Setting
from orangewidget import gui
from orangewidget.utils.widgetpreview import WidgetPreview
import Orange.data
from Orange.data.pandas_compat import table_from_frame

import pandas as pd
import requests
from difflib import SequenceMatcher, get_close_matches
from mecoda_minka import get_obs, get_dfs


taxon_url = "https://raw.githubusercontent.com/eosc-cos4cloud/mecoda-orange/master/mecoda_orange/data/taxon_tree_with_marines.csv"
taxon_tree = pd.read_csv(taxon_url)


def _get_tree_from_ancestry(obs):
    ancestries = []
    for ob in obs:
        ancestries.append(ob.taxon_ancestry)
    unique_ancestries = list(set(ancestries))
    if len(unique_ancestries) > 1:
        match = SequenceMatcher(None, unique_ancestries[0], unique_ancestries[1]).find_longest_match(
            0, len(unique_ancestries[0]), 0, len(unique_ancestries[1]))
        common_string = unique_ancestries[0][match.a:match.a + match.size]
    else:
        common_string = unique_ancestries[0]

    # delete last number not complete in the match and the last /
    common_string = common_string.rsplit("/", 1)[0]
    numbers = common_string.split("/")

    if "1" in numbers:
        numbers.remove("1")

    tree = []

    for number in numbers:
        number = int(number)
        name = taxon_tree[taxon_tree['taxon_id']
                          == number]['taxon_name'].item()
        rank = taxon_tree[taxon_tree['taxon_id'] == number]['rank'].item()
        tree.append(f"{rank} {name}")

    return " <br>>> ".join(tree)


def _get_id_from_name(taxon_name):
    taxon_name = taxon_name.replace(" ", "%20")
    taxon_name = taxon_name.capitalize()
    url = f"https://minka-sdg.org/taxon_names.json?name={taxon_name}"
    taxon_id = requests.get(url).json()[0]['taxon_id']
    return taxon_id


def _get_id_from_wikipedia(name_search):
    names = []
    searches = requests.get(
        f"https://es.wikipedia.org/w/api.php?action=query&list=search&srprop=snippet&format=json&origin=*&utf8=&srsearch={name_search}").json()['query']['search']

    for search in searches:
        names.append(search['title'])

    for name in names:
        try:
            taxon_id = _get_id_from_name(name)
            taxa_url = f"https://minka-sdg.org/taxa/{taxon_id}.json"
            obs_count = requests.get(taxa_url).json()['observations_count']
            if obs_count > 0:
                return taxon_id, name
        except:
            continue


def get_obs_from_common_name(name_search):
    try:
        name_clean = name_search.replace(" ", "%20")
        taxon_id = _get_id_from_name(name_clean)
        sci_name = taxon_tree[taxon_tree['taxon_id']
                              == taxon_id]['taxon_name'].item()
        print(taxon_id, sci_name)
        obs = get_obs(taxon_id=taxon_id)
        if len(obs) > 0:
            ancestry = _get_tree_from_ancestry(obs)
        else:
            ancestry = ""
    except:
        try:
            taxon_id, sci_name = _get_id_from_wikipedia(name_search)
            print(taxon_id, sci_name)
            taxa_url = f"https://minka-sdg.org/taxa/{taxon_id}.json"
            obs_count = requests.get(taxa_url).json()['observations_count']
            if obs_count > 0:
                print("Option 2:", sci_name)
                obs = get_obs(taxon_id=taxon_id)
                if len(obs) > 0:
                    ancestry = _get_tree_from_ancestry(obs)

        except:
            sci_name = requests.get(
                f"https://es.wikipedia.org/w/api.php?action=query&list=search&srprop=snippet&format=json&origin=*&utf8=&srsearch={name_search}").json()['query']['search'][0]['title']
            options = get_close_matches(
                sci_name, taxon_tree.taxon_name.to_list())
            taxon_id = _get_id_from_name(options[0])
            taxa_url = f"https://minka-sdg.org/taxa/{taxon_id}.json"
            obs_count = requests.get(taxa_url).json()['observations_count']
            if obs_count > 0:
                print("Option 3:", options[0])
                obs = get_obs(taxon_id=taxon_id)
                if len(obs) > 0:
                    ancestry = _get_tree_from_ancestry(obs)
                else:
                    ancestry = ""
            else:
                obs = []
                ancestry = ""
                sci_name = ""
    return obs, ancestry, sci_name


def get_obs_from_sci_name(name_search):
    try:
        taxon_id = _get_id_from_name(name_search)
        print(taxon_id)
        obs = get_obs(taxon_id=taxon_id)
        if len(obs) > 0:
            ancestry = _get_tree_from_ancestry(obs)
        else:
            ancestry = ""
            obs = []
    except:
        options = get_close_matches(
            name_search, taxon_tree.taxon_name.to_list())
        taxon_id = _get_id_from_name(options[0])
        taxa_url = f"https://minka-sdg.org/taxa/{taxon_id}.json"
        obs_count = requests.get(taxa_url).json()['observations_count']
        if obs_count > 0:
            print("Option 1:", options[0])
            taxon_id = _get_id_from_name(options[0])
            obs = get_obs(taxon_id=taxon_id)
            if len(obs) > 0:
                ancestry = _get_tree_from_ancestry(obs)
            else:
                ancestry = ""
        else:
            taxon_id = _get_id_from_name(options[1])
            taxa_url = f"https://minka-sdg.org/taxa/{taxon_id}.json"
            obs_count = requests.get(taxa_url).json()['observations_count']
            if obs_count > 0:
                print("Option 2:", options[1])
                taxon_id = _get_id_from_name(options[1])
                obs = get_obs(taxon_id=taxon_id)
                if len(obs) > 0:
                    ancestry = _get_tree_from_ancestry(obs)
                else:
                    ancestry = ""
            else:
                taxon_id = _get_id_from_name(options[2])
                taxa_url = f"https://minka-sdg.org/taxa/{taxon_id}.json"
                obs_count = requests.get(taxa_url).json()['observations_count']
                if obs_count > 0:
                    print("Option 3:", options[2])
                    taxon_id = _get_id_from_name(options[2])
                    obs = get_obs(taxon_id=taxon_id)
                    if len(obs) > 0:
                        ancestry = _get_tree_from_ancestry(obs)
                    else:
                        ancestry = ""
                else:
                    options = taxon_tree[taxon_tree.taxon_name.str.contains(
                        name_search)].name.to_list()
                    if len(options) > 0:
                        for option in options:
                            try:
                                possible_id = _get_id_from_name(option)
                                taxa_url = f"https://minka-sdg.org/taxa/{possible_id}.json"
                                obs_count = requests.get(taxa_url).json()[
                                    'observations_count']
                                if obs_count > 0:
                                    taxon_id = possible_id
                                    print("Option 4:", option)
                                    obs = get_obs(taxon_id=taxon_id)
                                    if len(obs) > 0:
                                        ancestry = _get_tree_from_ancestry(obs)
                            except:
                                ancestry = ""
                                obs = []
                                taxon_id = ""
                    else:
                        ancestry = ""
                        obs = []
                        taxon_id = ""
    taxon_name = taxon_tree[taxon_tree.taxon_id == taxon_id].taxon_name.item()
    return obs, ancestry, taxon_name


class TaxonWidget(OWBaseWidget):
    # Widget's name as displayed in the canvas
    name = "Minka Taxon Search"

    # Short widget description
    description = "Get observations from Minka filtered by scientific or common name."

    # An icon resource file path for this widget
    icon = "icons/leaf-solid-minka.png"

    # Priority in the section MECODA
    priority = 4

    # Basic (convenience) GUI definition:
    #   a simple 'single column' GUI layout
    want_main_area = False

    #   with a fixed non resizable geometry.
    resizing_enabled = False

    # Defining settings
    taxon_common = Setting("", schema_only=True)
    taxon_sci = Setting("", schema_only=True)

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

        self.infoa = gui.widgetLabel(info, '\
            Here you can search observation by scientific or common name<br>\
            to filter observations from <a href="https://minka-sdg.org">minka-sdg.org</a>.')
        self.infob = gui.widgetLabel(info, 'No observations fetched yet.')

        gui.separator(self.controlArea)

        # searchBox area
        self.searchBox = gui.widgetBox(
            self.controlArea,
            "Search fields",
        )

        self.taxon_sci_line = gui.lineEdit(
            self.searchBox,
            self,
            "taxon_sci",
            label="Scientific name:",
            controlWidth=200,
            orientation=1,
        )

        self.taxon_common_line = gui.lineEdit(
            self.searchBox,
            self,
            "taxon_common",
            label="Common name:",
            controlWidth=200,
            orientation=1,
        )

        # commit area
        self.commitBox = gui.widgetBox(self.controlArea, "", spacing=2)
        gui.button(self.commitBox, self, "Load", callback=self.commit)

    def commit(self):
        self.infoa.setText('Searching...')
        self.infob.setText(f'')
        try:
            progress = gui.ProgressBar(self, 2)
            progress.advance()
            if self.taxon_common != "":
                obs, ancestry, sci_name = get_obs_from_common_name(
                    self.taxon_common)
            elif self.taxon_sci != "":
                obs, ancestry, sci_name = get_obs_from_sci_name(self.taxon_sci)
            if len(obs) > 0:
                self.df_obs, self.df_photos = get_dfs(obs)

                self.df_obs.taxon_name = pd.Categorical(self.df_obs.taxon_name)
                self.df_obs.order = pd.Categorical(self.df_obs.order)
                self.df_obs.family = pd.Categorical(self.df_obs.family)
                self.df_obs.genus = pd.Categorical(self.df_obs.genus)
                print(self.df_obs.head())

                self.df_obs['taxon_name'] = self.df_obs['taxon_name'].str.lower()
                self.df_photos['taxon_name'] = self.df_photos['taxon_name'].str.lower(
                )

                self.infoa.setText(
                    f'Found: <b>{sci_name}</b><br>>> {ancestry}')
                self.infob.setText(
                    f'{len(self.df_obs):,} observations | {len(self.df_photos):,} photos')

                self.Outputs.observations.send(table_from_frame(self.df_obs))

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


if __name__ == "__main__":
    WidgetPreview(TaxonWidget).run()
