### Collector for UNICEF SAM's Datasets
[![Build Status](https://github.com/OCHA-DAP/hdx-scraper-unicef-sam/workflows/build/badge.svg)](https://github.com/OCHA-DAP/hdx-scraper-unicef-sam/actions?query=workflow%3Abuild) [![Coverage Status](https://coveralls.io/repos/github/OCHA-DAP/hdx-scraper-unicef-sam/badge.svg?branch=master&ts=1)](https://coveralls.io/github/OCHA-DAP/hdx-scraper-unicef-sam?branch=master)

Collector designed to collect UNICEF SAM datasets from the [UNICEF SAM](https://www.unicef.org/appeals/covid-19/situation-reports) website 
and to automatically register datasets on the 
[Humanitarian Data Exchange](http://data.humdata.org/) project.

### Usage
python run.py

For the script to run, you will need to either pass in your HDX API key as a parameter or have a file called .hdx_configuration.yml in your home directory containing your HDX key eg.

    hdx_key: "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    hdx_read_only: false
    hdx_site: test
    
 You will also need to pass in your user agent as a parameter or pass a parameter *user_agent_config_yaml* specifying where your user agent file is located. It should be of the form:
 
    user_agent: MY_USER_AGENT
    
 If you have many user agents, you can create a file of this form, put its location in *user_agent_config_yaml* and specify the lookup in *user_agent_lookup*:
 
    myscraper:
        user_agent: MY_USER_AGENT
    myscraper2:
        user_agent: MY_USER_AGENT2

 Note for HDX scrapers: there is a universal .useragents.yml file you should use.

 Alternatively, you can set up environment variables eg. for production runs: USER_AGENT, HDX_KEY, HDX_SITE, BASIC_AUTH, EXTRA_PARAMS, TEMP_DIR, LOG_FILE_ONLY
