# Read data/matched_dict.json and data/APS_plant_diseases.csv

#%%
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
import pandas as pd
import json
from pathlib import Path
from fuzzywuzzy import process
# from datasets import Dataset, DatasetDict
from pandas import Series
from tqdm import tqdm

#%%
tuplify = lambda arr: tuple(i if type(i) in (str,type(None)) else tuple(i) for i in arr if i or i is None) if arr else ()
#%%
t_q = str
t_q_guaranteed = str
t_eppo = str
t_eppo_guaranteed = str
t_sparql_response = List[Optional[Dict]]
t_raw_sparql_response = Dict[str,Dict[str,List]]
t_triplet = Tuple[str,Optional[t_q],Optional[t_eppo]]
t_triplet_list = List[t_triplet]

#%%
# Read datasheets/*.md

data_dir = Path("datasheets")
datasheet_files = list(data_dir.glob("*.md"))
datasheet_files
#%%
datasheet_names = [f.stem for f in datasheet_files]
datasheet_names

#%%
# 0/0

# Get downloadable eppo files here: https://data.eppo.int/
# You need one called Bayer

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
        name = _eppo_df[_eppo_df.fullname==trg[0]].fullname.iloc[0]
        return name, eppo
        

#%%

#%%
#%% Load data
data_dir = Path("data")
with open(data_dir / "matched_dict.json", "r") as f:
    matched_dict = json.load(f)
df_aps = pd.read_csv(data_dir / "APS_plant_diseases.csv")

#%%

matched_dict


#%%
# matched_dict
#%%
#%% Read data elsewhere
data = dict() or data
#%%
classes = list(data)
classes

dataset_dict = dict()

in_aps = [] # classes from dataset that are found in APS csv
in_eppo = [] # fullnames from aps that are found in EPPO
in_datasheet = [] # eppo codes that are found in datasheets

for klass in tqdm(classes):
    print("=== Processing class:", klass)
    found = set()
    
    print("=Searching in APS dataset...")
    for i in df_aps.iloc:
        i:Series
        if i.Afflict.lower() == klass:
            found.add(i["Full plant name"])
    if not found:
        print(f"-Not found in APS dataset: {klass}")
        continue
    fn = list(found)[0] # found full name
    print(f"+Found in APS dataset: {fn}")
    in_aps.append(klass)
    
    fn_clean = fn.split("(")[1].strip(") ")
    fn_clean

    print(f"=Searching in eppo for: {fn_clean}")
    res = search_local_eppo_name(fn_clean)
    if not res:
        print(f"-Not found in eppo: {fn_clean}")
        continue
    propper_fullname, eppo = res
    print(f"+Found in eppo: {propper_fullname} -> {eppo}")
    in_eppo.append(propper_fullname)
    print(f"=Searching in datasheets for: {eppo}")
    there = eppo in datasheet_names
    if there:
        print(f"+Exists: {eppo}.md")
        in_datasheet.append(eppo)
    else:
        print(f"-Not found: {eppo}.md")
#%%

classes = list(data)
classes

in_aps = [] # classes from dataset that are found in APS csv
in_eppo = [] # fullnames from aps that are found in EPPO
in_datasheet = [] # eppo codes that are found in datasheets

for klass in tqdm(classes):
    
    print("=== Processing class:", klass)
    found = list()

    print("=Searching in APS dataset...")
    for i in df_aps.iloc:
        i:Series
        if i.Afflict.lower() == klass:
            # found.add(i["Full plant name"])
            # found.add(dict(i))
            found.append(i)
    if not found:
        print(f"-Not found in APS dataset: {klass}")
        continue

    fn = found[0]["Full plant name"] # found full name
    print(f"+Found in APS dataset: {fn}")
    # in_aps.append(klass)

    fn_clean = fn.split("(")[1].strip(") ")
    fn_clean, len(found)

    dataset_dict[klass] = dataset_dict.get(klass, dict())
    dataset_dict[klass]["Name"] = klass
    dataset_dict[klass]["Fullname"] = fn_clean

    
    dataset_dict["Diseases"] = dict()
    for f in tqdm(found, leave=False):
        
        dis_name = f["Disease"]
        dataset_dict["Diseases"][dis_name] = dict()
        # dataset_dict["Diseases"][dis_name]["Pathogens"] = [iss.split("(")[0].replace("Genus","").lower() for iss in f["Pathogen"].split("\n")]
        dataset_dict["Diseases"][dis_name]["Pathogens"] = []
        pathogens  = [iss.strip().lower().split("(")[0].replace("genus","") for iss in f["Pathogen"].replace(",","\n").split("\n")]
        dataset_dict["Diseases"][dis_name]["Afflict"] = f["Afflict"]
        
        founds = []
        for pathogen in tqdm(set(pathogens), leave=False):
            print(f"- Searching eppo for pathogen: {pathogen}")
            res = search_local_eppo_name(pathogen) # (name, eppo)
            if not res:
                print(f"  - Not found in eppo: {pathogen}")
            else:
                founds.append((pathogen, res))
                # propper_fullname, eppo = res
                print(f"  + Found in eppo: {propper_fullname} -> {eppo}")

        founds
        for fs in founds:
            pathogen, (propper_fullname, eppo) = fs
            paths = dataset_dict["Diseases"][dis_name]["Pathogens"] 
            dataset_dict["Diseases"][dis_name]["Pathogens"].append({
                "Queried": pathogen,
                "Fullname": propper_fullname,
                "EPPO": eppo
            })
        
        # break
    dataset_dict

#%%
dataset_dict = dict()

klass = classes[19]



print("=== Processing class:", klass)
found = list()

print("=Searching in APS dataset...")
for i in df_aps.iloc:
    i:Series
    if i.Afflict.lower() == klass:
        # found.add(i["Full plant name"])
        # found.add(dict(i))
        found.append(i)
if not found:
    print(f"-Not found in APS dataset: {klass}")
    raise ValueError()

fn = found[0]["Full plant name"] # found full name
print(f"+Found in APS dataset: {fn}")
# in_aps.append(klass)

fn_clean = fn.split("(")[1].strip(") ")
fn_clean, len(found)

dataset_dict[klass] = dataset_dict.get(klass, dict())
dataset_dict[klass]["Name"] = klass
dataset_dict[klass]["Fullname"] = fn_clean

#%%
# dataset_dict["Diseases"] = dict()
# for f in found:
    
#     dis_name = f["Disease"]
#     dataset_dict["Diseases"][dis_name] = dict()
#     # dataset_dict["Diseases"][dis_name]["Pathogens"] = [iss.split("(")[0].replace("Genus","").lower() for iss in f["Pathogen"].split("\n")]
#     dataset_dict["Diseases"][dis_name]["Pathogens"] = []
#     pathogens  = [iss.split("(")[0].replace("Genus","").lower() for iss in f["Pathogen"].split("\n")]
#     dataset_dict["Diseases"][dis_name]["Afflict"] = f["Afflict"]
    
#     founds = []
#     for pathogen in tqdm(set(pathogens)):
#         print(f"- Searching eppo for pathogen: {pathogen}")
#         res = search_local_eppo_name(pathogen) # (name, eppo)
#         if not res:
#             print(f"  - Not found in eppo: {pathogen}")
#         else:
#             founds.append((pathogen, res))
#             # propper_fullname, eppo = res
#             print(f"  + Found in eppo: {propper_fullname} -> {eppo}")

#     founds
#     for fs in founds:
#         pathogen, (propper_fullname, eppo) = fs
#         paths = dataset_dict["Diseases"][dis_name]["Pathogens"] 
#         dataset_dict["Diseases"][dis_name]["Pathogens"].append({
#             "Queried": pathogen,
#             "Fullname": propper_fullname,
#             "EPPO": eppo
#         })
    
#     # break
# dataset_dict

#%%
with open ("data/test_datasetlet_2.json", 'w+') as fd:
    json.dump(dataset_dict,fd,indent=4)
#%%

s_found
#%%
flat_pathogens = [p for s in s_found for p in s["Pathogens"]]
flat_pathogens
founds = []
for pathogen in tqdm(set(flat_pathogens)):
    print(f"- Searching eppo for pathogen: {pathogen}")
    res = search_local_eppo_name(pathogen)
    if not res:
        print(f"  - Not found in eppo: {pathogen}")
    else:
        founds.append((pathogen, res))
        # propper_fullname, eppo = res
        print(f"  + Found in eppo: {propper_fullname} -> {eppo}")

founds
#%%
len(s_found)
#%%

#%%

#%%
print(f"=Searching in eppo for: {fn_clean}")
res = search_local_eppo_name(fn_clean)
if not res:
    print(f"-Not found in eppo: {fn_clean}")
    raise ValueError()
propper_fullname, eppo = res
print(f"+Found in eppo: {propper_fullname} -> {eppo}")
# in_eppo.append(propper_fullname)

#%%
print(f"=Searching in datasheets for: {eppo}")
there = eppo in datasheet_names
if there:
    print(f"+Found datasheet: {eppo}.md")
    in_datasheet.append(eppo)
else:
    print(f"-Not found datasheet: {eppo}.md")

#%%