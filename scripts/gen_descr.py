
#%%


import base64
import json

from tqdm import tqdm
import requests
#%%


#%%


with open("data/matched_dict.json",'r+') as fd:
    matched_dict = json.load(fd)

#%%


matched_dict

#%%

datasetlets = {}

# Iterate files in datasetlet folder
import pathlib
datasetlet_folder = pathlib.Path("datasetlet")
for file in datasetlet_folder.glob("*.md"):
    with open(file,'r+') as fd:
        datasetlet = json.load(fd)
        datasetlets[file.stem] = datasetlet
#%%
datasetlets
#%%
hosts = [i.lower() for i in {it["host"] for it in datasetlets.values()}]
#%%
host_files_dict = {}

for host in tqdm(hosts):
    # host = hosts[0]
    diss = list(matched_dict[host])
    host_files_dict[host] = {}
    for disease in tqdm(diss, leave=False):
        # disease = diss[0]
        paths = matched_dict[host][disease]["wild_path"] + \
        matched_dict[host][disease]["pdoc_path"] + \
        matched_dict[host][disease]["pvil_path"]
        # Iterate dirs from paths to get all file paths
        file_paths = []
        for path in paths:
            file_paths.extend(list(pathlib.Path(path).rglob("*")))
        file_paths
        file_dicts = [{"file_path":fp} for fp in file_paths]
        host_files_dict[host][disease] = file_dicts
#%%
list(host_files_dict)
all_files = []
for host in host_files_dict:
    for disease in host_files_dict[host]:
        all_files.extend(host_files_dict[host][disease])

len(all_files)

#%%

### Start ollama code
#%%

# ---- JSON-ориентированный промпт ----
# PROMPT_TEMPLATE = f"""
# Determine the plant class and the plant disease class shown in the image.
# If the model’s confidence for any category is below 70%, return the class "undefined".

# Respond ONLY in valid JSON with the following structure:

# {{
#   "plant_class": "<name or 'undefined'>",
#   "disease_class": "<name or 'undefined'>",
#   "plant_confidence": <number from 0 to 100>,
#   "disease_confidence": <number from 0 to 100>,
#   "explanation": "<short explanation>"
# }}
# """

#%%
# DATASET_DIR = Path(r"datasets\PlantDoc-Dataset-windows-compatible\train")   # папка с изображениями
# OUTPUT_CSV = "classification_results.csv"
# MODEL_NAME = "qwen2.5vl:3b"
MODEL_NAME = "gemma3:27b"


class OllamaVisionAnalyzer:
    # def __init__(self, model="qwen2.5vl:3b", host="http://localhost:11434"):
    def __init__(self, model="gemma3:27b", host="http://localhost:11434"):
        self.model = model
        self.host = host
    
    def encode_image(self, image_path):
        """Convert image to base64 encoding"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path, image_class= None
):
        
        """Send image to Ollama for analysis"""
        
        prompt=f"""Determine the plant disease of the plant shown in the image.
                        Plant class is presumably: {image_class}
                        Give detailed explanation of the disease symptoms. Pay attention to leaf, stem, fruit symptoms, any spots or other visible signs.
                        Explainations should not contain disease name. It should only describe the symptoms.

                        Respond in the following format:
                        Disease class: <name>
                        Disease confidence: <percentage from 0 to 100>
                        Explanation: <what are signs of the disease in the image>
                        """
        
        # Encode the image
        image_data = self.encode_image(image_path)
        
        # Prepare the request
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        }
        
        # Make the API call
        response = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"API Error: {response.status_code}")
#%%
# Usage example
analyzer = OllamaVisionAnalyzer(model=MODEL_NAME, host="http://192.168.42.156:11434")
#%%
file_path = host_files_dict["apple"]["scab"][0]["file_path"]
file_path
# as str
file_path.as_posix()
#%%
for host in tqdm(host_files_dict):
    for disease in tqdm(host_files_dict[host],
                        leave=False):
        for file in tqdm(host_files_dict[host][disease],
                         leave=False):
            if "description" in file:
                continue    
            description = analyzer.analyze_image(file["file_path"], image_class=host)
            file["description"] = description                             
            
            with open ("data/ollama_descriptions.json",'w+') as fd:
                json.dump(host_files_dict,fd, indent=2)
                
# all_files[0]["file_path"]
#%%

#%%
# description = analyzer.analyze_image(file_path
# , image_class="apple")

#%%

### Stop ollama code

#%%
