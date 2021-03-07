#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for UNICEF SAM.

"""
from os.path import join

import pytest
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country
from hdx.utilities.path import temp_dir
from hdx.data.vocabulary import Vocabulary
from unicef import (
    generate_dataset_and_showcase,
    get_countriesdata,
    get_all_countriesdata,
    join_reports,
    concat_reports,
    hxltags_from_config
)


class TestScraperName:
    countrydata1 = [
        {
            "REF_AREA": "AFG",
            "Geographic area": "Afghanistan",
            "SITREP_INDICATOR": "CV-01-01",
            "TIME_PERIOD": "2020-4-9",
            "OBS_VALUE": "1",
            "DATA_SOURCE": "Source1",
            "TARGET": "2",
        }
    ]
    countrydata2 = [
        {
            "REF_AREA": "AFG",
            "Geographic area": "Afghanistan",
            "SITREP_INDICATOR": "CV-01-02",
            "TIME_PERIOD": "2020-4-9",
            "OBS_VALUE": "3",
            "DATA_SOURCE": "Source1",
            "TARGET": "4",
        }
    ]

    @pytest.fixture(scope="function")
    def configuration(self):
        Configuration._create(
            hdx_read_only=True,
            user_agent="test",
            project_config_yaml=join("tests", "config", "project_configuration.yml"),
        )
        Locations.set_validlocations(
            [{"name": "afg", "title": "Afghanistan"}]
        )  # add locations used in tests
        Country.countriesdata(False)
        Vocabulary._tags_dict = True
        Vocabulary._approved_vocabulary = {
            "tags": [{"name": "hxl"}, {"name": "xxx"}, {"name": "yyy"}],
            "id": "4e61d464-4943-4e97-973a-84673c1aaa87",
            "name": "approved",
        }
        return Configuration

    @pytest.fixture(scope="function")
    def config(self):
        import yaml

        with open(join("tests", "config", "project_configuration.yml")) as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    @pytest.fixture(scope="function")
    def downloader(self):
        class Downloader:
            @staticmethod
            def get_tabular_rows(url, *args, **kwargs):
                if url == "http://url1":
                    return (
                        sorted(TestScraperName.countrydata1[0].keys()),
                        TestScraperName.countrydata1,
                    )
                if url == "http://url2":
                    return (
                        sorted(TestScraperName.countrydata2[0].keys()),
                        TestScraperName.countrydata2,
                    )
                raise Exception(f"Requested url {url} not supported")

        return Downloader()

    def test_get_countriesdata(self, downloader):
        countriesdata, headers = get_countriesdata("http://url1", downloader)
        assert countriesdata["AFG"] == TestScraperName.countrydata1
        assert countriesdata["world"] == TestScraperName.countrydata1

    def test_get_all_countriesdata(self, downloader, config):
        countries, countriesdata, headers = get_all_countriesdata(config, downloader)
        assert set(c["iso3"] for c in countries) == set(["AFG", "world"])
        assert set(c["name"] for c in countries) == set(["Afghanistan", "World"])
        assert countriesdata["AFG"]["CV_01_01"] == TestScraperName.countrydata1
        assert countriesdata["world"]["CV_01_01"] == TestScraperName.countrydata1
        assert countriesdata["AFG"]["CV_01_02"] == TestScraperName.countrydata2
        assert countriesdata["world"]["CV_01_02"] == TestScraperName.countrydata2

    def test_join_reports(self, downloader, config):
        countries, countriesdata, headers = get_all_countriesdata(config, downloader)
        rows, headers = join_reports(countriesdata["AFG"], config)
        assert len(rows) == 1
        assert rows[0]["observation_field1"]=='1'
        assert rows[0]["target_field1"]=='2'
        assert rows[0]["observation_field2"]=='3'
        assert "target_field2" not in rows[0]

    def test_concat_reports(self, downloader, config):
        countries, countriesdata, headers = get_all_countriesdata(config, downloader)
        rows, headers = concat_reports(countriesdata["AFG"])
        assert len(rows) == 2
        assert rows[0]["OBS_VALUE"]=='1'
        assert rows[0]["TARGET"]=='2'
        assert rows[1]["OBS_VALUE"]=='3'
        assert rows[1]["TARGET"]=='4'

    def test_hxltags_from_config(self, config):
        tags = hxltags_from_config(config)
        assert tags == dict(
            observation_field1="#observation_field1",
            target_field1="#target_field1",
            observation_field2="#observation_field2",
        )

#    def test_generate_dataset_and_showcase(self, configuration, downloader, config):
#        countries, countriesdata, headers = get_all_countriesdata(config, downloader)
#        country = [c for c in countries if c["iso3"]=="AFG"][0]
#        countrydata = countriesdata[country["iso3"]]
#        with temp_dir('scrapername') as folder:  # if you need a temporary folder that will be deleted
#            dataset, showcase = generate_dataset_and_showcase(folder, country, countrydata, headers, config)
#            assert dataset == {...}
#
#            resources = dataset.get_resources()
#            assert resources == [...]
#
#            assert showcase == {...}
