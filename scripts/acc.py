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

# project_root = Path(__file__).resolve().parents[1]  # scripts/.. -> project root
project_root = Path("./")
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
    # and pic_data.get("disease") == pic_data.get("res_disease")
)
num_of_pics, num_of_matches, num_of_matches / num_of_pics

#%%
num_of_matches2 = 0
for plant_name, diseases in data.items():
    for disease_name, pic_files in diseases.items():
        for pic_name, pic_data in pic_files.items():

            if pic_data.get("res_plant") == plant_name and pic_data.get("res_disease") == disease_name:
                num_of_matches2 += 1
           
print(num_of_matches2, num_of_pics, num_of_matches2/num_of_pics)
#%%

acc = num_of_matches2/num_of_pics

#%% 

# Среднеклассовые accuracy, recall, f1-score

#%%
# Get unique classes
unique_classes = set()
for plant_name, diseases in data.items():
    for disease_name in diseases.keys():
        unique_classes.add((plant_name, disease_name))

unique_classes_dict = {}
for uclass in unique_classes:
    unique_classes_dict[uclass] = []

for plant_name, diseases in tqdm(data.items()):
    for disease_name, pic_files in diseases.items():
        for pic_name, pic_data in pic_files.items():
            unique_classes_dict[(plant_name, disease_name)].append(pic_data)

#%%

per_class_accuracy = {}
per_class_recall = {}
per_class_f1 = {}

#%%

class_stats = {}

for uclass in tqdm(unique_classes):
    class_accuracy = 0
    class_precision = 0
    class_recall = 0
    class_f1 = 0
    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    
    for plant_name, diseases in tqdm(data.items(), leave=False):
        for disease_name, pic_files in diseases.items():
            for pic_name, pic_data in pic_files.items():
                res_plant = pic_data.get("res_plant")
                res_disease = pic_data.get("res_disease")
                pred_plant = uclass[0]
                pred_disease = uclass[1]
                
                if res_plant == uclass[0] and res_disease == uclass[1]:
                    # actual positive
                    if pred_plant == uclass[0] and pred_disease == uclass[1]:
                        tp += 1
                    else:
                        fn += 1
                else:
                    # actual negative
                    if pred_plant == uclass[0] and pred_disease == uclass[1]:
                        fp += 1
                    else:
                        tn += 1
    class_accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
    class_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    class_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    class_f1 = 2 * (class_precision * class_recall) / (class_precision + class_recall) if (class_precision + class_recall) > 0 else 0
    class_stats[uclass[0]] = {
        "accuracy": class_accuracy,
        "precision": class_precision,
        "recall": class_recall,
        "f1": class_f1
    }

#%%
class_stats 
#%%
mean_class_stats = {
    "accuracy": sum(stat["accuracy"] for stat in class_stats.values()) / len(class_stats),
    "precision": sum(stat["precision"] for stat in class_stats.values()) / len(class_stats),
    "recall": sum(stat["recall"] for stat in class_stats.values()) / len(class_stats),
    "f1": sum(stat["f1"] for stat in class_stats.values()) / len(class_stats)
}
mean_class_stats


#$$

list(data["tomato"]["late blight"]["8634f13d-ee5a-442e-8b58-6b667c91379c___GHLB2 Leaf 8968.JPG.json"])  # list diseases for tomato)
#%%

with open("data/matched_dict.json", "r", encoding="utf-8") as fd:
    matched_dict = json.load(fd)
#%%
matched_dict

ds = ('PlantDoc-Dataset-windows-compatible', 'PlantVillage-Dataset', 'plantwild_v2')


#%%

ds_dict_acc = {k:[] for k in ds}

for plant_name, diseases in tqdm(data.items()):
    for disease_name, pic_files in tqdm(diseases.items(), leave=False):
        for pic_name, pic_data in pic_files.items():
            dataset = pic_data["file"].split("/")[1]
            ds_dict_acc[dataset].append(pic_data)

list(ds_dict_acc)
#%%
for k,v in ds_dict_acc.items():
    print(k, len(v))
#%%

"""
Calculate accuracy per dataset
"""

#%%
for d in ds:
    num_of_pics = len(ds_dict_acc[d])
    num_of_matches = sum(
        1
        for pic_data in ds_dict_acc[d]
        if pic_data.get("plant") == pic_data.get("res_plant")
        and pic_data.get("disease") == pic_data.get("res_disease")
    )
    print(d, num_of_pics, num_of_matches, num_of_matches / num_of_pics)

#%%
all_pics = [pic_data for plant_map in data.values() for pic_map in plant_map.values() for pic_data in pic_map.values()]
num_of_pics = len(all_pics)
num_of_matches = sum(
    1
    for pic_data in all_pics
    if pic_data.get("plant") == pic_data.get("res_plant")
    and pic_data.get("disease") == pic_data.get("res_disease")
)
num_of_pics, num_of_matches, num_of_matches / num_of_pics
#%%
"""
Calculate per-class per-dataset accuracy, precision, recall, f1-score
"""

#%%

#%%
stats_dict = {}

for d in tqdm(ds):
    stats_dict[d] = {}
    for uclass in tqdm(unique_classes, leave=False):
        class_accuracy = 0
        class_precision = 0
        class_recall = 0
        class_f1 = 0
        tp = 0
        fp = 0
        tn = 0
        fn = 0


        for pic_data in ds_dict_acc[d]:
            dataset = pic_data["file"].split("/")[1]
            if dataset != d:
                continue
            res_plant = pic_data.get("res_plant")
            res_disease = pic_data.get("res_disease")
            pred_plant = uclass[0]
            pred_disease = uclass[1]
            
            if res_plant == uclass[0] and res_disease == uclass[1]:
                # actual positive
                if pred_plant == uclass[0] and pred_disease == uclass[1]:
                    tp += 1
                else:
                    fn += 1
            else:
                # actual negative
                if pred_plant == uclass[0] and pred_disease == uclass[1]:
                    fp += 1
                else:
                    tn += 1
        class_accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        class_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        class_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        class_f1 = 2 * (class_precision * class_recall) / (class_precision + class_recall) if (class_precision + class_recall) > 0 else 0
        num = tp + fn
        if num != 0:
            stats_dict[d][uclass] = {
                "accuracy": class_accuracy,
                "precision": class_precision,
                "recall": class_recall,
                "f1": class_f1,
                "num": num
            }
stats_dict
#%%
stats_dict
#%%
mean_stats_dict = {}   

for d in ds:
    mean_stats_dict[d] = {
        "accuracy": sum(stat["accuracy"] for stat in stats_dict[d].values()) / len(stats_dict[d]),
        "precision": sum(stat["precision"] for stat in stats_dict[d].values()) / len(stats_dict[d]),
        "recall": sum(stat["recall"] for stat in stats_dict[d].values()) / len(stats_dict[d]),
        "f1": sum(stat["f1"] for stat in stats_dict[d].values()) / len(stats_dict[d]),
        "num": len(stats_dict[d])
    }
mean_stats_dict
#%%

for d in ds:
#%%
pics = {ds:[pic_data for plant_map in data.values() for pic_map in plant_map.values() for pic_data in pic_map.values() if pic_data["file"].split("/")[1] == d] for d in ds}
len(pics)

#%%

for d in ds:
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

ds_dict = {}

# per_dataset_accuracy = {}
# per_dataset_precision = {}
# per_dataset_recall = {}
# per_dataset_f1 = {}

ds_class_stats = {}

for d in tqdm(ds):
    
    for uclass in tqdm(unique_classes, leave=False):
    
        class_accuracy = 0
        class_precision = 0
        class_recall = 0
        class_f1 = 0
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        
        
        for plant_name, diseases in tqdm(data.items(), leave=False):
            for disease_name, pic_files in diseases.items():
                for pic_name, pic_data in pic_files.items():
                    res_plant = pic_data.get("res_plant")
                    res_disease = pic_data.get("res_disease")
                    pred_plant = uclass[0]
                    pred_disease = uclass[1]
                    
                    if res_plant == uclass[0] and res_disease == uclass[1]:
                        # actual positive
                        if pred_plant == uclass[0] and pred_disease == uclass[1]:
                            tp += 1
                        else:
                            fn += 1
                    else:
                        # actual negative
                        if pred_plant == uclass[0] and pred_disease == uclass[1]:
                            fp += 1
                        else:
                            tn += 1
        class_accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        class_precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        class_recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        class_f1 = 2 * (class_precision * class_recall) / (class_precision + class_recall) if (class_precision + class_recall) > 0 else 0
        class_stats[uclass[0]] = {
            "accuracy": class_accuracy,
            "precision": class_precision,
            "recall": class_recall,
            "f1": class_f1
        }

for plant_name, diseases in data.items():
    for disease_name, pic_files in diseases.items():
        for pic_name, pic_data in pic_files.items():
            dataset = pic_data["file"].split("/")[1]
            ds.add(dataset)
            # print(pic_name)
            # print(pic_data)
            # raise ValueError("Stop")
            # key = f"{plant_name}___{disease_name}___{pic_name}"
            # if key in matched_dict:
            #     pic_data["matched"] = matched_dict[key]
            # else:
            #     pic_data["matched"] = False

