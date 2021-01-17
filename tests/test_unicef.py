#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
Unit tests for UNICEF SAM.

'''
from os.path import join

import pytest
from hdx.hdx_configuration import Configuration
from hdx.hdx_locations import Locations
from hdx.location.country import Country
from hdx.utilities.path import temp_dir
from hdx.data.vocabulary import Vocabulary
from unicef import generate_dataset_and_showcase, get_countriesdata


class TestScraperName:
    countrydata = {...}

    @pytest.fixture(scope='function')
    def configuration(self):
        Configuration._create(hdx_read_only=True, user_agent='test',
                              project_config_yaml=join('tests', 'config', 'project_configuration.yml'))
        Locations.set_validlocations([{'name': 'afg', 'title': 'Afghanistan'}])  # add locations used in tests
        Country.countriesdata(False)
        Vocabulary._tags_dict = True
        Vocabulary._approved_vocabulary = {'tags': [{'name': 'hxl'}, {'name': 'xxx'}, {'name': 'yyy'}], 'id': '4e61d464-4943-4e97-973a-84673c1aaa87', 'name': 'approved'}

    @pytest.fixture(scope='function')
    def downloader(self):
        class Response:
            @staticmethod
            def json():
                pass

        class Download:
            @staticmethod
            def download(url):
                response = Response()
                if url == 'http://xxx':
                    def fn():
                        return {'key': [TestScraperName.countrydata]}
                    response.json = fn
                return response
        return Download()

    def test_get_countriesdata(self, downloader):
        countries, countriesdata, headers = get_countriesdata('http://xxx/', downloader)
        assert countriesdata == [TestScraperName.countrydata]

    def test_generate_dataset_and_showcase(self, configuration, downloader):
        with temp_dir('scrapername') as folder:  # if you need a temporary folder that will be deleted
            dataset, showcase = generate_dataset_and_showcase(downloader, folder, TestScraperName.countrydata)
            assert dataset == {...}

            resources = dataset.get_resources()
            assert resources == [...]

            assert showcase == {...}

