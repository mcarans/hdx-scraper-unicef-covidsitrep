from liquer import *
import pandas as pd
import re
from glob import glob
from lxml import etree
from urllib.request import urlopen
from liquer.ext.lq_pandas import df_from

DATA_FOLDER = "out/"
FILENAME_PREFIX = "covid19sitrep_"

@first_command
def data(country="world"):
    return pd.read_csv(DATA_FOLDER+FILENAME_PREFIX+country+".csv")

@first_command
def all_countries():
    pattern = FILENAME_PREFIX+r"([a-zA-Z0-9]+)\.csv"
    return sorted([re.search(pattern,f).group(1) for f in glob(DATA_FOLDER+FILENAME_PREFIX+"*.csv") if re.search(pattern,f) is not None])

@first_command
def unicef_codes_xml():
    return urlopen("https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/codelist/UNICEF.EMOPS/CL_EMOPS_INDICATORS/1.0").read()

@command
def unicef_codes_df(xml):
    df = pd.DataFrame(columns=["identifier", "text", "urn"])
    root = etree.fromstring(xml)
    for x in root.xpath("//*[local-name() = 'Code']"):
        df = df.append(
        dict(
            urn=x.attrib["urn"],
            identifier=x.attrib["id"],
            text="".join(xx.text for xx in x)),
            ignore_index=True
        )
        #print(x, x.tag, x.attrib["urn"], x.attrib["id"], "".join(xx.text for xx in x))
    return df

@first_command
def sitrep(*code):
    c = "-".join(code)
    url = f"https://sdmx.data.unicef.org/ws/public/sdmxapi/rest/data/UNICEF.EMOPS,DF_SITREP_COVID19,1.0/.{c}?format=csv"
    print(f"Read situational report from {url}")
    return df_from(url,"csv").get()

@command
def unique_count(df):
    d={}
    for c in df.columns:
        v = list(df[c].unique())
        d[f"{c}_count"]=len(v)
        d[f"{c}_value"]=v[0]
    return d

@command
def unique_stat(df):
    data=[]
    for i, row in df.iterrows():
        d=unique_count(sitrep(row.identifier))
        d["identifier"]=row.identifier
        d["text"]=row.text
        data.append(d)
    return pd.DataFrame(data)


if __name__ == '__main__':
    df = evaluate("unicef_codes_xml/unicef_codes_df").get()
#    for i, row in df.iterrows():
#        print(row.text)
#        evaluate_and_save(f"sitrep-{row.identifier}/{row.identifier.replace('-','_')}.xlsx")

    evaluate_and_save(f"unicef_codes_xml/unicef_codes_df/unique_stat/unique_stat.xlsx")
