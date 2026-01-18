#%%

import json
from pathlib import Path
from markdown_it import MarkdownIt

#%%
data_dir = Path("datasheets")
datasheet_files = list(data_dir.glob("*.md"))
datasheet_files

datasheet_names = [f.stem for f in datasheet_files]
datasheet_names

#%%

with open("data/test_datasetlet_2.json","r+") as fd:
    dataset_dict_2 = dataset_dict = json.load(fd)
    
#%%



#%%

diss = dataset_dict_2["Diseases"]
diss

diss2 = {k:v for k,v in diss.items() if v.get("Pathogens")}
diss2



diss3 = {k:v for k,v in diss.items() if any([patho["EPPO"] in datasheet_names for patho in v["Pathogens"]])}
diss3
#%%
ds = []

for k,v in diss3.items():
    for patho in v["Pathogens"]:
        ds.append({"host":v.get("Afflict"), "disease": k, "pathogen": patho.get("Fullname"), "pathogen_eppo": patho.get("EPPO")})
ds
#%%

ds

#%%
## Same with 5

with open("data/test_datasetlet_5.json","r+") as fd:
    dataset_dict_5 = dataset_dict = json.load(fd)
    
#%%
dataset_dict_5["Diseases"]
#%%
diss = dataset_dict_5["Diseases"]
diss
diss2 = {k:v for k,v in diss.items() if v.get("Pathogens")}
diss2


diss3 = {k:v for k,v in diss.items() if any([patho["EPPO"] in datasheet_names for patho in v["Pathogens"]])}
diss3
#%%

ds1 = []

for k,v in diss3.items():
    for patho in v["Pathogens"]:
        ds1.append({"host":v.get("Afflict"), "disease": k, "pathogen": patho.get("Fullname"), "pathogen_eppo": patho.get("EPPO")})
ds1
ds.extend(ds1[:-1])
#%%
ds
#%%
static_symptoms = {}
#%%
for d in ds:
    d["symptoms"] = static_symptoms.get(d["pathogen_eppo"], "").replace("\n"," ")

ds
#%%
# create datasetlet directory
import os
os.makedirs("datasetlet", exist_ok=True)
#%%

for d in ds:
    with open(f"datasetlet/{d['pathogen_eppo']}.md","w+") as fd:
        json.dump(d,fd, indent=2)
        
## Extract md symptoms

ds_eppos = [v["pathogen_eppo"] for v in ds]
ds_eppos
#%%

#%%
#%%
#%%



ld1 = [pathos for diss in dataset_dict["Diseases"].values() for pathos in diss.get("Pathogens")]

eppos = [el.get("EPPO") for el in ld1]

mm = [(name,name in datasheet_names) for name in eppos if name in datasheet_names]
mm
#%%

#%%

#%%
#%%

with open("data/test_datasetlet_5.json","r+") as fd:
    dataset_dict = json.load(fd)

data_dir = Path("datasheets")
datasheet_files = list(data_dir.glob("*.md"))
datasheet_files

datasheet_names = [f.stem for f in datasheet_files]
datasheet_names

ld1 = [pathos for diss in dataset_dict["Diseases"].values() for pathos in diss.get("Pathogens")]

eppos = [el.get("EPPO") for el in ld1]

mm = [(name,name in datasheet_names) for name in eppos if name in datasheet_names]
mm

#%%