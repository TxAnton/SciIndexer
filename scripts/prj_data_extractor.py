#%%
from pathlib import Path
import requests
import json
import os
from tqdm import tqdm
import subprocess
import shutil

#%%
#%%

# API_KEY = os.getenv("OPENAI_API_KEY") or API_KEY # or paste your key as a string
API_KEY = os.getenv("OPENAI_API_KEY") # or paste your key as a string

def chat(query):
    url = "https://api.openai.com/v1/responses"

    headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

    payload = {
    "model": "gpt-4.1-mini",
    "input": query
}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["output"][0]['content'][0]["text"]

#%%
url = 'https://gtr.ukri.org/gtr/api/projects.json'

#%%

out_path = Path("data/grant_data.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
#%%
response = requests.get(url)
response
#%%
with open(out_path, 'wb') as f:
    f.write(response.content)
print(f"Data saved to {out_path}")

#%%

# read out_path
with open(out_path, 'r') as f:
    data = json.load(f)
type(data)

#%%
#%%


# if data_pure:
#     raise ValueError("data_pure already exists, please restart the kernel to avoid contamination")

not_available_text = "Abstracts are not currently available"

data_pure = []

for prj in data["project"]:
    abstract = prj.get("abstractText")

    if not abstract or not_available_text in abstract:
        continue
    
    data_pure.append({
        "id": prj.get("id"),
        "orig_title": prj.get("title"),
        "abstract": abstract,
    })

len(data_pure)
#%%

data_pure[0]
#%%
q_make_title="""
Given the following research project abstract, generate a concise and informative title for the project.
Abstract: {abstract}
Title:
"""
#%%


#%%
for datum in tqdm(data_pure):
    # datum = data_pure[0]
    if datum.get("generated_title"):
        continue
    prompt = q_make_title.format(abstract=datum["abstract"])
    title = chat(prompt)
    datum["generated_title"] = title
#%%
## Prepare dataset for graph rag

# Each datum will be expotrted as a separate json file
# Before that it should be modified to contain only id, generated_title, abstract

#%%

data_export = []

for datum in data_pure:
    data_export.append({
        "id": datum["id"],
        "title": datum["generated_title"],
        "abstract": datum["abstract"],
    })
#%%
data_pure
#%%
base_path = Path("grag/grant_data_graph_rag/input")
base_path.mkdir(parents=True, exist_ok=True)
#%%
for datum in tqdm(data_export):
    file_path = base_path / f"{datum['id']}.txt"
    with open(file_path, 'w') as f:
        f.write(json.dumps(datum))
#%%

## Graph RAG Functions:

grag_init = "graphrag init --root {root_path}"
grag_index = "graphrag index --root {root_path}"

grag_query_global = """
graphrag query \
--root "{root_path}" \
--method global \
--query "{query}" \
"""

grag_query_local = """
graphrag query \
--root "{root_path}" \
--method local \
--query "{query}" \
"""
#%%
def f_grag_init(root_path):
    cmd = grag_init.format(root_path=root_path)
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

def f_grag_index(root_path):
    cmd = grag_index.format(root_path=root_path)
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

def f_grag_query_global(root_path, query):
    cmd = grag_query_global.format(root_path=root_path, query=query)
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

def f_grag_query_local(root_path, query):
    cmd = grag_query_local.format(root_path=root_path, query=query)
    print(cmd)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

#%%

# Try to init grag/grant_data_graph_rag dir

init_path = Path("grag/grant_data_graph_rag")
init_path
#%%
res = f_grag_init(init_path)
res

#%%
# Dir "grag/data" Has right settings.yaml and .env files
# They should be copied to "grag/grant_data_graph_rag":

src_dir = Path("grag/data")
dst_dir = Path("grag/grant_data_graph_rag")

for file in ["settings.yaml", ".env"]:
    src_file = src_dir / file
    dst_file = dst_dir / file
    if src_file.exists():
        shutil.copy2(src_file, dst_file)
        print(f"Copied {src_file} to {dst_file}")
        
#%%
# Index graph from selected files
res_index = f_grag_index(init_path)
print(res_index)

#%%

q_get_doc_id = """Given search query return correct project id that corresponds by it's content
Query: '{query}'
Project id:
"""

#%%

matched = 0
s = len(data_pure)
for prj in data_pure:
    # prj = data_pure[0]
    prj
    title = prj["orig_title"]
    title
    q = q_get_doc_id.format(**{"query":title})
    res = f_grag_query_global(root_path=init_path,query=q)
    res
    orig_id = prj["id"]
    if res.lower() == orig_id.lower():
        matched+=1
    
acc = matched/s
#%%
#%%
#%%
#%%

import pandas as pd

df = pd.read_parquet("grag/grant_data_graph_rag/output/community_reports.parquet")
print(df.head())
#%%
df[["community","title","summary","full_content"]].to_csv("test.csv")
#%%
df.columns
#%%

