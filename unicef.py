#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
UNICEF SAM COVID-19:
-------------------

Reads UNICEF SAM COVID-19 csv and creates datasets.

"""

import logging

from hdx.data.dataset import Dataset
from hdx.data.showcase import Showcase
from hdx.location.country import Country
from hdx.utilities.dictandlist import dict_of_lists_add
from slugify import slugify

logger = logging.getLogger(__name__)


hxltags = {
    "REF_AREA": "#country+code",
    "Geographic area": "#country+name",
    "Situation Report Indicator": "#indicator+name",
    "SITREP_INDICATOR": "#indicator+code",
    "HAC_PILLAR": "#indicator+type+code",
    "Humanitarian Action for Children Pillar": "#indicator+type+name",
    "UNIT_MEASURE": "#indicator+unit+code",
    "Unit of measure": "#indicator+unit+name",
    "TIME_PERIOD": "#date",
    "OBS_VALUE": "#indicator+value+num",
    "DATA_SOURCE": "#meta+source",
    "TARGET": "#indicator+target+num",
    "OBS_STATUS": "#indicator+status+code",
    "Observation status": "#indicator+status+name",
}

WORLD = "world"

def get_countriesdata(url, downloader, with_world=True):
    headers, iterator = downloader.get_tabular_rows(url, dict_form=True)
    countriesset = set()
    countriesdata = dict()
    if with_world:
        countriesset.add(WORLD)
    for row in iterator:
        countryiso3 = row["REF_AREA"]
        countriesset.add(countryiso3)
        countriesdata[countryiso3] = countriesdata.get(countryiso3, []) + [row]
        if with_world:
            countriesdata[WORLD] = countriesdata.get(WORLD, []) + [row]

    countries = list()
    for countryiso in sorted(list(countriesset)):
        if countryiso==WORLD:
            countries.append({"iso3": WORLD, "name": "World"})
        else:
            countryname = Country.get_country_name_from_iso3(countryiso)
            if countryname is None:
                continue
            countries.append({"iso3": countryiso, "name": countryname})
    return countries, countriesdata, headers


def generate_dataset_and_showcase(folder, country, countrydata, headers):
    countryname = country["name"]
    countryiso = country["iso3"].lower()
    if countryiso == WORLD:
        title = "Global COVID-19 Situation Report"
    else:
        title = "%s - COVID-19 Situation Report" % country["name"]
    logger.info("Creating dataset: %s" % title)
    name = "UNICEF SAM COVID-19 indicators for %s" % country["name"]
    slugified_name = slugify(name).lower()
    dataset = Dataset({"name": slugified_name, "title": title,})
#    dataset.set_maintainer("085d3bd8-9035-4b0e-9d2d-80e849dd7b07")
    dataset.set_maintainer("9957c0e9-cd38-40f1-900b-22c91276154b")
    dataset.set_organization("3ab17ac1-1196-4501-a4dc-a01d2e52ff7c")
    dataset.set_subnational(False)
    dataset.set_expected_update_frequency("Every month")
    dataset.add_tags(["hxl", "children", "COVID-19", "malnutrition"])

    if countryiso == WORLD:
        dataset.add_other_location("world")
    else:
        try:
            dataset.add_country_location(countryiso)
        except HDXError:
            logger.error(f"{countryname} ({countryiso})  not recognised!")
            return None, None

    filename = "covid19sitrep_%s.csv" % countryiso
    resourcedata = {
        "name": "COVID-19 indicators for %s" % countryname,
        "description": "COVID-19 Situation Report",
        "countryiso":countryiso,
        "countryname":countryname
    }
    success, results = dataset.generate_resource_from_iterator(
        headers,
        countrydata,
        hxltags,
        "out",#folder,
        filename,
        resourcedata,
        datecol="TIME_PERIOD",
    )
    if success is False:
        logger.warning("%s has no data!" % name)
        return None, None

    showcase = Showcase(
        {
            "name": "%s-showcase" % slugified_name,
            "title": name,
            "notes": "Cases of severe acute malnutrition (SAM) and actions taken.",
            "url": "https://sites.unicef.org/nutrition/index_sam.html",
            "image_url": "https://sites.unicef.org/includes/images/unicef_for-every-child_EN.png",
        }
    )
    showcase.add_tags(["hxl", "children", "COVID-19", "malnutrition"])
    return dataset, showcase

