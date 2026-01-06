#!/usr/bin/env python3

from pathlib import Path
import json
from typing import Any, Dict
from tqdm import tqdm

#%%
"""
Read all JSON files from directory structure:
out/<plant>/<disease>/<pic#.json>

Saves results to a nested dict: {plant: {disease: {pic_name: data}}}
"""
#%%
# __file__, = !echo ${0}
__file__ = '/home/qius/Documents/Asp/Ha/code/plants_llm_vision/scripts/acc.py'

project_root = Path(__file__).resolve().parents[1]  # scripts/.. -> project root
out_path = project_root / "out"



#%%

"""
Traverse out_dir expecting structure: out/<plant>/<disease>/<pic#.json>
Returns nested dict: plant -> disease -> pic_filename -> parsed json
"""
out_dir = Path(out_path)
if not out_dir.exists():
    raise FileNotFoundError(f"Out directory does not exist: {out_dir}")
#%%

results: Dict[str, Dict[str, Dict[str, Any]]] = {}

for plant_dir in tqdm(  sorted(out_dir.iterdir()), desc="Plants"):
    if not plant_dir.is_dir():
        # print(f"Skipping non-directory: {plant_dir}")
        continue
    plant_name = plant_dir.name
    results.setdefault(plant_name, {})

    for disease_dir in tqdm(sorted(plant_dir.iterdir()), desc="Diseases", leave=False):
        if not disease_dir.is_dir():
            # print(f"Skipping non-directory: {disease_dir}")
            continue
        disease_name = disease_dir.name
        results[plant_name].setdefault(disease_name, {})

        for pic_file in sorted(disease_dir.iterdir()):
            if not pic_file.is_file():
                continue
            if pic_file.suffix.lower() != ".json":
                continue
            try:
                with pic_file.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception as exc:
                # skip unreadable/invalid json but continue processing
                print(f"Warning: failed to read {pic_file}: {exc}")
                continue
            results[plant_name][disease_name][pic_file.name] = data
data:Dict[str, Dict[str, Dict[str, Any]]] = results
#%%
list(data["tomato"]["late blight"]["8634f13d-ee5a-442e-8b58-6b667c91379c___GHLB2 Leaf 8968.JPG.json"])  # list diseases for tomato)
# ['file',
#  'plant',
#  'disease',
#  'res_plant',
#  'res_disease',
#  'res_plant_confidence',
#  'res_disease_confidence',
#  'error',
#  'proc_time',
#  'worker']
#%%
data["tomato"]["late blight"]["8634f13d-ee5a-442e-8b58-6b667c91379c___GHLB2 Leaf 8968.JPG.json"]
#%%
num_of_pics = sum(len(pic_map) for plant_map in data.values() for pic_map in plant_map.values())
num_of_pics
num_of_matches = sum(
    1
    for plant_map in data.values()
    for pic_map in plant_map.values()
    for pic_data in pic_map.values()
    if pic_data.get("plant") == pic_data.get("res_plant")
    and pic_data.get("disease") == pic_data.get("res_disease")
)
num_of_pics, num_of_matches, num_of_matches / num_of_pics

#%%
#%%
num_of_matches2 = 0
for plant_name, diseases in data.items():
    for disease_name, pic_files in diseases.items():
        for pic_name, pic_data in pic_files.items():
            # print(pic_name, pic_data)

            if pic_data.get("res_plant") == plant_name and pic_data.get("res_disease") == disease_name:
                num_of_matches2 += 1
            # print(pic_data.get("plant"), plant_name)
            # raise ValueError("stop")
        # print(f"  {plant_name}/{disease_name}: {len(pic_files)} files")
# num_of_matches2
# num_of_matches2/num_of_pics
print(num_of_matches2, num_of_pics, num_of_matches2/num_of_pics)
#%%
# simple summary output
total = sum(
    len(pic_map) for plant_map in data.values() for pic_map in plant_map.values()
)
print(f"Loaded {total} JSON files from '{out_path}'")
# Example: show counts per plant/disease
for plant, diseases in data.items():
    for disease, pics in diseases.items():
        print(f"  {plant}/{disease}: {len(pics)} files")