#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Top level script. Calls other functions that generate datasets that this script then creates in HDX.

"""
import logging
from os.path import join, expanduser

from hdx.hdx_configuration import Configuration
from hdx.utilities.downloader import Download
from hdx.utilities.path import progress_storing_tempdir

from unicef import generate_dataset_and_showcase, get_all_countriesdata

from hdx.facades.simple import facade

logger = logging.getLogger(__name__)


lookup = "hdx-scraper-unicef-sam"


def main():
    """Generate dataset and create it in HDX"""

    with Download() as downloader:
        config=Configuration.read()
        project_config = {key:value for key,value in config.items() if key.startswith("CV")}
        qc_indicators = config.get("qc_indicators",{})
        countries, countriesdata, headers = get_all_countriesdata(
                project_config, downloader
            )

        logger.info("Number of datasets to upload: %d" % len(countries))
        for info, country in progress_storing_tempdir("UNICEFSAM", countries, "iso3"):
            dataset, showcase, bites_disabled = generate_dataset_and_showcase(
                info["folder"], country, countriesdata[country["iso3"]], headers, project_config, qc_indicators
            )
            if dataset:
                dataset.update_from_yaml()
                dataset.create_in_hdx(
                    remove_additional_resources=True,
                    hxl_update=False,
                    updated_by_script="HDX Scraper: UNICEF Sam",
                    batch=info["batch"],
                )
                dataset.generate_resource_view(-1, bites_disabled=bites_disabled, indicators=qc_indicators)
                showcase.create_in_hdx()
                showcase.add_dataset(dataset)


if __name__ == "__main__":
    facade(
        main,
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yml"),
        user_agent_lookup=lookup,
        project_config_yaml=join("config", "project_configuration.yml"),
    )
