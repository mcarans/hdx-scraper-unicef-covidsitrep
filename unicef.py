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
    """Fetch the countries data from an url and split them by country."""
    headers, iterator = downloader.get_tabular_rows(url, dict_form=True)
    countriesdata = dict()
    for row in iterator:
        countryiso3 = row["REF_AREA"]
        countriesdata[countryiso3] = countriesdata.get(countryiso3, []) + [row]
        if with_world:
            countriesdata[WORLD] = countriesdata.get(WORLD, []) + [row]

    return countriesdata, headers


def countries_from_iso_list(countriesset):
    """
    Create a list of dictionaries describing each country in the countriesset.
    The countriesset is a list or set of iso3 country identifiers.
    Output list contains a dictionary with "iso3" and "name" of a country.
    """
    countries = list()
    for countryiso in sorted(list(countriesset)):
        if countryiso == WORLD:
            countries.append({"iso3": WORLD, "name": "World"})
        else:
            countryname = Country.get_country_name_from_iso3(countryiso)
            if countryname is None:
                continue
            countries.append({"iso3": countryiso, "name": countryname})
    return countries


def get_all_countriesdata(config, downloader, with_world=True):
    countriesset = set()
    countriesdata = {}
    headers = {}
    for report_id, report_config in config.items():
        logger.info("Getting situation report %s" % report_id)
        url = report_config["url"]
        report_countriesdata, report_headers = get_countriesdata(url, downloader)
        countriesset.update(report_countriesdata.keys())
        headers[report_id] = report_headers
        for countryiso, data in report_countriesdata.items():
            countriesdata[countryiso] = countriesdata.get(countryiso,{})
            countriesdata[countryiso][report_id] = data

    return countries_from_iso_list(countriesset), countriesdata, headers

def join_reports(countrydata, config):
    key_fields = ["REF_AREA", "Geographic area", "TIME_PERIOD", "DATA_SOURCE"]
    data = {}
    headers = key_fields[:]

    for report_id, report_rows in countrydata.items():
        for report_row in report_rows:
            report_config = config.get(report_id,{})
            key = tuple(report_row[field] for field in key_fields)
            joined_row = data.get(key, {})
            for field_type, source_field in (("observation_field", "OBS_VALUE"), ("target_field", "TARGET")):
                if field_type in report_config:
                    destination_field = report_config[field_type]
                    joined_row[destination_field] = report_row[source_field]
                    if destination_field not in headers:
                        headers.append(destination_field)
            data[key]=joined_row

    rows = []
    for key_values, joined_values in data.items():
        row_key = dict(zip(key_fields, key_values))
        rows.append({**row_key, **joined_values})
    return rows, headers



def generate_dataset_and_showcase(folder, country, countrydata, headers, config):
    countryname = country["name"]
    countryiso = country["iso3"].lower()
    if countryiso == WORLD:
        title = "Global COVID-19 Situation Report"
    else:
        title = "%s - COVID-19 Situation Report" % country["name"]
    logger.info("Creating dataset: %s" % title)
    name = "UNICEF COVID-19 situation report indicators for %s" % country["name"]
    slugified_name = slugify(name).lower()
    dataset = Dataset({"name": slugified_name, "title": title,})
    #    dataset.set_maintainer("085d3bd8-9035-4b0e-9d2d-80e849dd7b07")
    dataset.set_maintainer("9957c0e9-cd38-40f1-900b-22c91276154b")
    dataset.set_organization("3ab17ac1-1196-4501-a4dc-a01d2e52ff7c")
    dataset.set_subnational(False)
    dataset.set_expected_update_frequency("Every month")
    dataset.add_tags(
        [
            "hxl",
            "children",
            "COVID-19",
            "malnutrition",
            "hygiene",
            "health",
            "healthcare",
        ]
    )

    if countryiso == WORLD:
        dataset.add_other_location("world")
    else:
        try:
            dataset.add_country_location(countryiso)
        except HDXError:
            logger.error(f"{countryname} ({countryiso})  not recognised!")
            return None, None

    joined_rows, joined_headers = join_reports(countrydata, config)

    filename = "covid19sitrep_joined_%s.csv" % countryiso

    resourcedata = {
        "name": "Joined COVID-19 Situation Report Data - %s" % (countryname),
        "description": "Data joined from all situational reports",
        "countryiso": countryiso,
        "countryname": countryname,
    }
    success, results = dataset.generate_resource_from_iterator(
        joined_headers,
        joined_rows,
        hxltags,
        "out",  # folder,
        filename,
        resourcedata,
        datecol="TIME_PERIOD",
    )
    if success is False:
        logger.warning("Joined resource %s has no data!" % filename)

    for report_id in countrydata.keys():
        resource_config = config[report_id]
        filename = resource_config["filename"] + "_%s.csv" % countryiso
        logger.info("Creating resource %s for report %s in %s" % (filename,report_id,countryiso))
        resourcedata = {
            "name": "%s - %s" % (resource_config["name"], countryname),
            "description": resource_config["description"],
            "countryiso": countryiso,
            "countryname": countryname,
        }
        success, results = dataset.generate_resource_from_iterator(
            headers[report_id],
            countrydata[report_id],
            hxltags,
            "out",  # folder,
            filename,
            resourcedata,
            datecol="TIME_PERIOD",
        )
        if success is False:
            logger.warning("%s has no data!" % filename)

    showcase = Showcase(
        {
            "name": "%s-showcase" % slugified_name,
            "title": name,
            "notes": "UNICEF Situation Reports for COVID19 including severe acute malnutrition (SAM) and actions taken.",
            "url": "https://sites.unicef.org/nutrition/index_sam.html",
            "image_url": "https://sites.unicef.org/includes/images/unicef_for-every-child_EN.png",
        }
    )
    showcase.add_tags(
        [
            "hxl",
            "children",
            "COVID-19",
            "malnutrition",
            "hygiene",
            "health",
            "healthcare",
        ]
    )
    return dataset, showcase
