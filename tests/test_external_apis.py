import datetime
import os

import Orange.data
import pandas as pd

# import pyodcollect.occore as occore
# import pyodcollect.ocmodels as ocmodels
import pytest
import requests
from mecoda_minka import get_dfs, get_obs
from Orange.data.pandas_compat import table_from_frame

from mecoda_orange.canAIRio_fixed import get_fixed_stations_data
from mecoda_orange.canAIRio_fixed_extra_info import get_historic_data_fixed_station
from mecoda_orange.canAIRio_mobile import get_mobile_stations
from mecoda_orange.canAIRio_mobile_extra_info import get_mobile_track
from mecoda_orange.minka_marine_filter import get_marine
from mecoda_orange.minka_search_taxa import (
    get_obs_from_common_name,
    get_obs_from_sci_name,
)
from mecoda_orange.minka_taxa import get_descendants


@pytest.fixture(name="observations", scope="session")
def observations():
    return get_obs(num_max=20)


@pytest.fixture(name="taxon_tree", scope="session")
def taxon_tree():
    taxon_url = "https://raw.githubusercontent.com/eosc-cos4cloud/mecoda-orange/master/mecoda_orange/data/taxon_tree_with_marines.csv"
    df_taxon_tree = pd.read_csv(taxon_url)
    return df_taxon_tree


def test_minka_widget(observations):
    df_obs, df_photos = get_dfs(observations)
    df_obs["taxon_name"] = df_obs["taxon_name"].str.lower()
    df_photos["taxon_name"] = df_photos["taxon_name"].str.lower()

    table_obs = table_from_frame(df_obs)
    table_photos = table_from_frame(df_photos)
    for meta in table_photos.domain.metas:
        if meta.name == "photos_medium_url":
            meta.attributes = {"type": "image"}

    assert len(df_obs) <= len(df_photos)
    assert type(table_obs) == Orange.data.table.Table
    assert [
        meta.attributes
        for meta in table_photos.domain.metas
        if meta.name == "photos_medium_url"
    ] == [{"type": "image"}]
    assert len(df_obs.columns) == 26
    assert len(table_obs) == 20


def test_marine_filter():
    taxon_url = "https://raw.githubusercontent.com/eosc-cos4cloud/mecoda-orange/master/mecoda_orange/data/taxon_tree_with_marines.csv"
    df_taxon_tree = pd.read_csv(taxon_url)
    marine_df = df_taxon_tree[["taxon_id", "rank", "marine"]]
    observations = get_obs(
        num_max=40,
        year=2021,
    )
    df_obs, df_photos = get_dfs(observations)
    df_obs["taxon_name"] = df_obs["taxon_name"].str.lower()
    df_obs = df_obs[df_obs.taxon_id.notnull()].reset_index(drop=True)
    df_obs["taxon_id"] = df_obs.taxon_id.astype(int)
    df_complete = df_obs.merge(marine_df, how="left", on="taxon_id")
    df = df_complete[df_complete["quality_grade"] == "research"]
    marines_df = df[df.marine == True]
    terrestrials_df = df[df.marine == False]
    marines = table_from_frame(marines_df)
    terrestrials = table_from_frame(terrestrials_df)

    assert len(df) == len(marines) + len(terrestrials)
    assert type(marines) == Orange.data.table.Table
    if len(marines_df) > 0:
        assert get_marine(marines_df.taxon_name.iloc[0]) == True


def test_get_images(observations):
    df_obs2, df_photos2 = get_dfs(observations)
    out = table_from_frame(df_photos2)
    for meta in out.domain.metas:
        if meta.name == "photos_medium_url":
            meta.attributes = {"type": "image"}

    assert len(out) == len(df_photos2)
    assert len(df_photos2) >= len(observations)
    assert type(out) == Orange.data.table.Table
    assert [
        meta.attributes for meta in out.domain.metas if meta.name == "photos_medium_url"
    ] == [{"type": "image"}]


# tests on minka_search_taxa
@pytest.mark.skip()
def test_get_obs_from_sci_name():
    name = "Peltodoris atromaculata"
    obs, ancestry, taxon_name = get_obs_from_sci_name(name)

    assert type(obs[0].created_at) == datetime.datetime
    assert ancestry.startswith("kingdom")
    assert taxon_name[0].isupper()


def test_get_obs_from_common_name():
    name = "pulpo"
    obs, ancestry, sci_name = get_obs_from_common_name(name)
    assert len(obs) > 0
    assert ancestry.startswith("kingdom")
    assert sci_name[0].isupper()


# tests on minka_taxa
def test_get_descendants(taxon_tree):
    for name in ["Edmundsella", "Tripterygiidae", "Gadiformes"]:
        taxa = get_descendants(name, taxon_tree)
        assert len(taxa) > 1
        assert taxa[0] == ""
        assert taxa[1][0].isupper()


def test_minka_taxa(taxon_tree):
    name = "Asterina gibbosa"
    id_selected = taxon_tree[taxon_tree["taxon_name"] == name].taxon_id.item()
    obs = get_obs(taxon_id=id_selected)
    assert len(obs) > 0
    assert type(obs[0].created_at) == datetime.datetime
    assert obs[0].quality_grade in ["casual", "research", "needs_id"]
    assert type(obs[0].user_id) == int


# tests on odour_collect
@pytest.mark.skip()
def test_odour_collect():
    date_init = "2019-01-01"
    date_end = str(datetime.date.today())
    minAnnoy = -4
    maxAnnoy = 4
    minIntensity = 0
    maxIntensity = 6
    type_ = 0
    subtype = 0

    # convert date_init and date_end to datetime format
    if type(date_init) == str:
        init = datetime.datetime.strptime(date_init, "%Y-%m-%d").date()
    else:
        init = date_init

    if type(date_end) == str:
        end = datetime.datetime.strptime(date_end, "%Y-%m-%d").date()
    else:
        end = date_end

    requestparams = ocmodels.OCRequest(
        date_init=init,
        date_end=end,
        minAnnoy=minAnnoy,
        maxAnnoy=maxAnnoy,
        minIntensity=minIntensity,
        maxIntensity=maxIntensity,
        type=type_,
        subtype=subtype,
    )
    observations = occore.get_oc_data(requestparams, gpscoords=None)
    observations[["longitude", "latitude"]] = observations[
        ["longitude", "latitude"]
    ].astype(float)
    observations[["time_hour", "time_min", "time_sec"]] = observations.time.astype(
        str
    ).str.split(":", expand=True)

    table_oc = table_from_frame(observations)

    assert len(table_oc) > 11000
    assert type(table_oc) == Orange.data.table.Table
    assert observations.dtypes["longitude"] == float
    assert len(observations.week_day.unique()) == 7
    assert observations.date.min() == init
    assert observations.date.max().year == end.year
    assert observations.type.value_counts().head(1).index[0] == "No Odour"
    assert observations.hedonic_tone_n.mean() < 0
    assert observations.intensity_n.median() > 2
    assert "time_hour" in observations.columns


# tests canAIRio widgets
def test_get_fixed_stations_data():
    observations = get_fixed_stations_data("PM1")
    table_canairio = table_from_frame(observations)
    assert len(observations) > 20
    assert len(observations.columns) == 19
    assert len(observations.geohash.unique()) > 10
    assert observations.measurementValue.max() > 5
    assert observations.measurementValue.min() == 0
    assert type(table_canairio) == Orange.data.table.Table


def test_get_historic_data_fixed_station():
    st = "EZTTTGOT77004A"
    obs = get_historic_data_fixed_station(st)
    assert len(obs) > 1
    assert obs.observedOn.max().year == datetime.datetime.now().year
    assert obs.license.unique()[0] == "CC BY-NC-SA"
    assert obs["decimalLatitude "].max() > 6
    assert obs["decimalLongitude "].unique()[0] == -2.88


def test_get_mobile_stations():
    obs = get_mobile_stations()
    assert len(obs) > 2000
    assert len(obs.columns) == 12
    assert obs.dtypes["lastLat"] == float
    assert obs.dtypes["P25"] == float


def test_get_mobile_track():
    obs = get_mobile_track("20200621210203")
    assert len(obs) == 10
    assert obs.dtypes["P25"] == int
    assert obs.dtypes["lat"] == float


# tests aire_ciudadano widget
@pytest.mark.skip()
def test_aireciudadano_last_query_response():
    query = '{job%3D"pushgateway"}'
    url = f"http://sensor.aireciudadano.com:30887/api/v1/query?query={query}"
    data = requests.get(url).json()["data"]["result"]
    df = pd.json_normalize(data)

    assert "value" in df.columns
    assert "CO2" in df["metric.__name__"].unique()
    assert len(df["metric.exported_job"].unique()) >= 70


@pytest.mark.skip()
def test_aireciudadano_range_query_response():
    start_datetime = "2022-12-01T12:00:00Z"
    end_datetime = "2022-12-01T13:00:00Z"
    query = '{job%3D"pushgateway"}'
    step = "10m"
    url = f"http://sensor.aireciudadano.com:30887/api/v1/query_range?query={query}&start={start_datetime}&end={end_datetime}&step={step}"
    data = requests.get(url).json()["data"]["result"]
    df = pd.json_normalize(data)

    assert "values" in df.columns
    assert "CO2" in df["metric.__name__"].unique()
    assert len(df["metric.exported_job"].unique()) >= 70
