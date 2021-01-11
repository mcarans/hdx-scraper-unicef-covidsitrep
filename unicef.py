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


hxltags = {'REF_AREA': '#country+code', 'Geographic area': '#country+name',
           'Situation Report Indicator': '#indicator+name', 'SITREP_INDICATOR': '#indicator+code',
           'HAC_PILLAR': '#indicator+type+code', 'Humanitarian Action for Children Pillar': '#indicator+type+name',
           'UNIT_MEASURE': '#indicator+unit+code', 'Unit of measure': '#indicator+unit+name',
           'TIME_PERIOD': '#date', 'OBS_VALUE': '#indicator+value+num', 'DATA_SOURCE': '#meta+source',
           'TARGET': '#indicator+target+num',
           'OBS_STATUS': '#indicator+status+code', 'Observation status': '#indicator+status+name'}

def get_countriesdata(url, downloader):
    headers, iterator = downloader.get_tabular_rows(url)
    countriesset = set()
    countriesdata = dict()
    for row in iterator:
        countryiso3 = row['REF_AREA']
        countriesset.add(countryiso3)
        dict_of_lists_add(countriesdata, countryiso3, row)
    countries = list()
    for countryiso in sorted(list(countriesset)):
        countryname = Country.get_country_name_from_iso3(countryiso)
        if countryname is None:
            continue
        countries.append({'iso3': countryiso, 'name': countryname})
    return countries, countriesdata, headers


def generate_dataset_and_showcase(folder, country, countrydata, headers):
    countryname = country['name']
    title = '%s - COVID-19 Situation Report' % country['name']
    logger.info('Creating dataset: %s' % title)
    name = 'UNICEF SAM COVID-19 indicators for %s' % countrydata['name']
    slugified_name = slugify(name).lower()
    dataset = Dataset({
        'name': slugified_name,
        'title': title,
    })
    dataset.set_maintainer('085d3bd8-9035-4b0e-9d2d-80e849dd7b07')
    dataset.set_organization('3ab17ac1-1196-4501-a4dc-a01d2e52ff7c')
    dataset.set_subnational(False)
    dataset.set_expected_update_frequency('Every month')
    filename = 'covid19sitrep_%s.csv' % country['iso3']
    resourcedata = {
        'name': 'COVID-19 indicators for %s' % countryname,
        'description': 'COVID-19 Situation Report'
    }
    success, results = dataset.generate_resource_from_iterator(
        headers, countrydata, hxltags, folder, filename, resourcedata,
        date_function=process_date)
    if success is False:
        logger.warning('%s for %s has no data!' % (category, countryname))
        continue
    resource.set_file_type('csv')  # set the file type to eg. csv
    dataset.add_update_resource(resource)

    showcase = Showcase({
        'name': '%s-showcase' % slugified_name,
        'title':
        'notes':
        'url':
        'image_url':
    })
    showcase.add_tags([])
    return dataset, showcase
