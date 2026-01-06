#%%
import sys
import os
import requests
# from SPARQLWrapper import SPARQLWrapper, JSON
import json
# import pandas as pd
# import numpy as np
from tqdm import tqdm
import time
from functools import lru_cache
# from bs4 import BeautifulSoup

from pathlib import Path
#%%

# JSON default serializer that knows how to convert Path and a few
# common numpy/pandas types into JSON-serializable Python primitives.
def json_default(o):
    # Local imports to avoid import-order problems if this file is executed
    # in a weird environment.
    from pathlib import Path as _Path
    import numpy as _np
    import pandas as _pd

    # pathlib.Path -> str
    if isinstance(o, _Path):
        return str(o)

    # numpy scalar types -> Python scalar
    if isinstance(o, (_np.integer, _np.floating, _np.bool_)):
        return o.item()

    # numpy arrays -> lists
    if isinstance(o, _np.ndarray):
        return o.tolist()

    # pandas Timestamp -> ISO string
    if isinstance(o, _pd.Timestamp):
        return o.isoformat()

    # bytes -> decode to utf-8 string
    if isinstance(o, (bytes, bytearray)):
        try:
            return o.decode('utf-8')
        except Exception:
            return str(o)

    if np.isnan(o):
        return 'null' 
    # Let json raise the TypeError for types we don't know how to serialize.
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


#%%

datadir = Path("datasets")
pwild_dir = "plantwild_v2"
pdoc_dir = 'PlantDoc-Dataset-windows-compatible'
pvil_dir = 'PlantVillage-Dataset'
#%%
d1 = datadir/pwild_dir
#%%
# list(d1.iterdir())
d1_classes =  set([i.name.lower() for i in d1.iterdir()])
d1_classes
d1_fullpath = [d1/i for i in d1_classes]
#%%
df_d1_classes = pd.DataFrame(columns=["fullpath","fullname","taxon","desease"], data=zip(
    d1_fullpath,
    d1_classes,
    [None]*len(d1_classes),
    [None]*len(d1_classes)))
df_d1_classes
#%%
d2 = datadir/pdoc_dir
list(d2.iterdir())
#%%
d2_classes = set()
d21_classes = set()
d22_classes = set()

d21 = d2/"train"
d22 = d2/"test"

# d21_classes.update([i.name for i in d21.iterdir()])
# d22_classes.update([i.name for i in d22.iterdir()])
d2_all = [(d21/i.name,i.name) for i in d21.iterdir()] + [(d22/i.name,i.name) for i in d22.iterdir()]
d2_all
#%%
d2_fullpaths, d2_classes = zip(*d2_all)
d2_fullpaths, d2_classes
# d2_classes = d21_classes.union
#%%
df_d2_classes = pd.DataFrame(columns=["fullpath","fullname","taxon","desease"], data=zip(
    d2_fullpaths,
    d2_classes,
    [None]*len(d2_classes),
    [None]*len(d2_classes)))
df_d2_classes

#%%
df_d1_classes = df_d1_classes.sort_values("fullname")
df_d2_classes = df_d2_classes.sort_values("fullname")
#%%

df_d1_classes.to_csv("data/d_wild_classes.csv",index=False)
df_d2_classes.to_csv("data/d_pdoc_classes.csv",index=False)
#%%
# extract taxons manually
#%%
df_d1_classes = pd.read_csv('data/d_wild_classes.csv', na_filter=False).reset_index(drop=True)
df_d2_classes = pd.read_csv('data/d_pdoc_classes.csv', na_filter=False).reset_index(drop=True)
#%%
def fill_desease(_df):
    for i in _df.index:
        name:str = _df.loc[i,"taxon"]
        fullname:str = _df.loc[i,"fullname"].lower()
        s_fullname = fullname.split(" ")
        name = s_fullname[0]
        if name == "bell" and s_fullname[1] == "pepper":
            name = "bell pepper"
        _name = name.replace('_'," ").split()
        _fullname = fullname.replace('_'," ").split()

        for j in _name:
            if j in _fullname:
                _fullname.remove(j)
            else:
                print(j, _fullname)
                raise Exception("wtf taxon name not in desease fullname")
        new_taxon = (' '.join(_name)).replace('soyabean','soybean')
        new_desease = (' '.join(_fullname)).replace('healty','healthy')
        _df.loc[i,"desease"] = new_desease
        _df.loc[i,"taxon"] = new_taxon

    return _df

df_d2_classes = fill_desease(df_d2_classes)
df_d1_classes = fill_desease(df_d1_classes)
#%%
df_d1_classes.to_csv("tmp.csv",index=False)
#%%
d3 = datadir/pvil_dir

d31 = d3/"raw"/"color"
# d32 = d3/"raw"/"segmented"
# d33 = d3/"raw"/"grayscale"
d_full = d31

list(d3.iterdir())
#%%
d3_all = set()

d3_all.update([(d_full/i.name,i.name) for i in d31.iterdir()])
d3_fullpath, d3_classes = zip(*d3_all)
d3_fullpath, d3_classes
#%%
# d3_classes.update([i.name for i in d31.iterdir()])
# d3_classes.update([i.name for i in d32.iterdir()])
# d3_classes.update([i.name for i in d33.iterdir()])

df_d3_classes1 = pd.DataFrame(columns=["fullpath","fullname","taxon","desease"], data=zip(
    d3_fullpath,
    d3_classes,
    [None]*len(d3_classes),
    [None]*len(d3_classes)))
df_d3_classes1

#%%

d3_classes_split = []

for ix in df_d3_classes1.index:
    fullpath = df_d3_classes1.loc[ix,"fullpath"]
    fullname = df_d3_classes1.loc[ix,"fullname"]
    _taxon,_deseases = fullname.split("___")
    
    taxon = ' '.join([i for i in _taxon.lower().split("_") if not ("(" in i or ")" in i)])
    taxon = taxon.replace("pepper, bell","bell pepper")
    deseases = [i.replace("_"," ").lower().removeprefix(taxon).replace('-',"").replace('  '," ").strip() for i in _deseases.split(" ")]
    # print(taxon,deseases)

    for d in deseases:
        d3_classes_split.append((fullpath,fullname,taxon,d,"pvil"))
    # break
    
d3_classes_split

df_d3_classes = df_d3_classes1 = pd.DataFrame(columns=["fullpath","fullname","taxon","desease","src"], data=d3_classes_split)
df_d3_classes
#%%

df_d1_classes["src"] = ['wild']*len(df_d1_classes)
df_d2_classes["src"] = ['pdoc']*len(df_d2_classes)


#%%


#%%
df_concat = pd.concat([df_d1_classes,df_d2_classes,df_d3_classes])
df_concat = df_concat.sort_values(['taxon','desease','fullname'])
df_concat.to_csv("data/d_concat_classes2.csv")
#%%
u_taxons = df_concat['taxon'].unique()
u_taxons
#%%

data = []

for taxon in u_taxons:
    _df = df_concat[df_concat["taxon"]==taxon]
    u_deseases = _df['desease'].unique()
    for desease in u_deseases:
        __df = _df[_df["desease"]==desease]
        _fullnames = __df["fullname"].to_list()
        pdoc_name = __df[__df["src"]=="pdoc"]["fullpath"].to_list()
        wild_name = __df[__df["src"]=="wild"]["fullpath"].to_list()
        pvil_name = __df[__df["src"]=="pvil"]["fullpath"].unique().tolist()
        _d = {"wild_name":wild_name,
              "pdoc_name":pdoc_name,
              "pvil_name":pvil_name,
              "taxon":taxon,
              "taxon_q":None,
              "taxon_eppo":None,
              "desease":desease,
              "desease_q":None}
        data.append(_d)
        # print(_fullnames)
        # break
    # break
len(data)
#%%
data
#%%
df_data1 = pd.DataFrame(data=data)
df_data1
#%%
def saveify(_df):
    _df = _df.copy()
    col = _df.columns
    for c in col:
        _df[c] = _df[c].apply(lambda x:json.dumps(x, default=json_default)).apply(lambda x:x if not x=="NaN" else 'null')
    return _df
#%%
# def saveify(_df):
#     _df = _df.copy()
#     col = _df.columns
#     for c in col:
#         _df[c] = _df[c].apply(lambda x:json.dumps(x))
#     return _df
#%%
df_data1_save = saveify(df_data1)
df_data1_save
#%%
df_data1_save.to_csv("data/d_corr13.csv",index=False)
#%%

from typing import Annotated, Dict, List, Literal, Optional, Tuple, Union
from fuzzywuzzy import process
t_q = str
t_q_guaranteed = str
t_eppo = str
t_eppo_guaranteed = str
t_sparql_response = List[Optional[Dict]]
t_raw_sparql_response = Dict[str,Dict[str,List]]
t_triplet = Tuple[str,Optional[t_q],Optional[t_eppo]]
t_triplet_list = List[t_triplet]
#%%

tuplify = lambda arr: tuple(i if type(i) in (str,type(None)) else tuple(i) for i in arr if i or i is None) if arr else ()
#%%
0/0

@lru_cache(maxsize=None)
def read_local_eppo():
    _df1 = pd.read_csv("eppo/gafname.txt")
    _df2 = pd.read_csv("eppo/gainame.txt")
    _df3 = pd.read_csv("eppo/pflname.txt")
    _df = pd.concat((_df1,_df2,_df3))    
    _names = _df["fullname"].dropna().tolist()
    return _df, _names

@lru_cache(maxsize=None)
def _search_local_eppo_names(name: str, limit) -> List[Tuple[str,int]]:
    _df,_names = read_local_eppo()
    column_as_list = _names
    res = tuplify(process.extract(name, column_as_list,limit=limit))
    
    return res

#%%

def search_local_eppo_name(name: str, limit = 20, _dfindings={}, threshold=90) -> Optional[t_eppo]:
    _eppo_df,_names = read_local_eppo()
    
    if name in _dfindings:
        _res = _dfindings[name]
    else:
        _res = _search_local_eppo_names(name, limit)
    trg = _res[0]
    
    if trg[1] <= threshold:
        return None
    else:
        eppo = _eppo_df[_eppo_df.fullname==trg[0]].code.iloc[0]
        return eppo

#%%

hosts_u_df = pd.read_csv("data/plant_taxonomy4_e.csv")
  
#%%
d_find_names = dict()
for taxon in tqdm(u_taxons):
    f_eppo = search_local_eppo_name(taxon)
    _df = hosts_u_df[hosts_u_df["eppo"]==f_eppo]
    if len(_df):
        _s = _df.iloc[0]
        eppo = _s["eppo"]
        q = _s["q"]
    else:
        eppo = q = None
    d_find_names[taxon] = (q,eppo)

d_find_names
    
#%%
df_data2 = df_data1.copy()


for i in df_data2.index:
    taxon = df_data1.loc[i,"taxon"]
    _t = d_find_names.get(taxon)
    if _t:
        df_data2.loc[i,"taxon_q"] = _t[0] if not type(_t[0])==float else None
        df_data2.loc[i,"taxon_eppo"] = _t[1]
    
df_data2
#%%
df_data2_save = saveify(df_data2)
df_data2_save
#%%
df_data2_save.to_csv("data/d_corr16.csv",index=False)

#%%
_df_data2 = df_data2.copy()
#%%
# df_data2.wild_name = df_data2.wild_name.apply(lambda x:bool(x))
# df_data2.pdoc_name = df_data2.pdoc_name.apply(lambda x:bool(x))
# df_data2.pvil_name = df_data2.pdoc_name.apply(lambda x:bool(x))
# df_data2
#%%
df_data2.to_csv("test.csv",index=False)
#%%

df_aps = pd.read_csv('data/APS_plant_diseases.csv', na_filter=False).reset_index(drop=True)

df_aps

#%%
# Нормализуем регистр
df_aps['Disease'] = df_aps['Disease'].str.lower().str.strip()
df_aps['Afflict'] = df_aps['Afflict'].str.lower().str.strip()

df_aps
#%%

matched = df_data2.merge(
    df_aps,
    left_on=['taxon', 'desease'],
    right_on=['Afflict', 'Disease'],
    how='left'
)

matched
#%%
matched.to_csv("test.csv",index=False)
#%%

from rapidfuzz import process, fuzz

def fuzzy_match_disease(row, aps_subset):
    if pd.notna(row['desease']):
        match = process.extractOne(
            row['desease'],
            aps_subset['Disease'],
            scorer=fuzz.token_sort_ratio
        )
        if match and match[1] > 85:
            return aps_subset.loc[aps_subset['Disease'] == match[0]].iloc[0]
    return pd.Series()
#%%
# Применяем для тех, кто не сматчился напрямую
unmatched = matched[matched['Category'].isna()]
fuzzy_results = unmatched.apply(lambda x: fuzzy_match_disease(x, df_aps), axis=1)
fuzzy_results
#%%
matched.update(fuzzy_results)

#%%
_matched = matched.copy()
#%%

matched["wild_path"]= matched["wild_name"]
matched["pdoc_path"]= matched["pdoc_name"]
matched["pvil_path"]= matched["pvil_name"]
matched["wild_name"] = matched["wild_name"].apply(lambda x: bool(x))
matched["pdoc_name"] = matched["pdoc_name"].apply(lambda x: bool(x))
matched["pvil_name"] = matched["pvil_name"].apply(lambda x: bool(x))

#%%
matched_save = saveify(matched)
#%%

matched_save.to_csv("data/d_corr19.csv",index=False)

#%%

taxons = matched["taxon"].unique().tolist()
taxons

#%%
# matched_todict = matched.to_dict(orient='records')
# matched_todict
#%%
matched_dict = {}
for taxon in taxons:
    
    _df_taxon = matched[matched["taxon"]==taxon]
    
    diseases = _df_taxon['desease'].unique().tolist()
    d = {}
    for disease in diseases:
        _df_desease = _df_taxon[_df_taxon["desease"]==disease]
        _json_desease = _df_desease.to_dict(orient='records')[0]
        # if len(_json_desease)>1:
        #     print(taxon,disease,_json_desease)
        d[disease] = _json_desease
    
    matched_dict[taxon] = d

#%%

with open("data/matched_dict.json",'w+') as fd:
    json.dump(matched_dict,fd, indent=4, default=json_default)
# matched_dict    
#%%

with open("data/matched_dict.json",'r+') as fd:
    matched_dict = json.load(fd)

# disease = matched_dict["wheat"]["leaf rust"]
disease = matched_dict["apple"]["scab"]
pathes = disease["wild_path"] + disease["pdoc_path"] + disease["pvil_path"]
# pathes
#%%
# all apple scab images
files = ([list(Path(i).iterdir()) for i in pathes])
flat_files = [item for sublist in files for item in sublist]
len(flat_files)
#%%


pathes = matched_dict["wheat"]["leaf rust"]["wild_path"] # ['datasets/plantwild_v2/wheat leaf rust']


#%%
for taxon in matched_dict:
    for desease in matched_dict[taxon]:
        print(taxon,desease)
        pathes = matched_dict[taxon][desease]["wild_path"] + matched_dict[taxon][desease]["pdoc_path"] + matched_dict[taxon][desease]["pvil_path"]
        files = ([list(Path(i).iterdir()) for i in pathes])
        flat_files = [item for sublist in files for item in sublist]
        print(f"  total images: {len(flat_files)}")


#%%



#%%