import os
import requests
import subprocess
from tqdm import tqdm

#%%
# Create directory for saving documents
output_dir = "datasheets_doc"
os.makedirs(output_dir, exist_ok=True)
#%%
# Dummy list of EPPO codes (replace with actual codes later)
# eppo_codes = ["TILLCO", "XYLEFA", "PHYPPN"]
eppo_codes = """
ALTEMA
BNYVV0
CERAFA
CERAFP
CORBMI
CORBSE
CRONCL
CRONCO
CRONQU
CRSPAN
CSVD00
DEUTTR
DIAPVA
DIBOMO
DITYDE
ENDCHA
ENDOPA
ERWIAM
GIBBCI
GLOMGO
GNOMUL
GREMAB
GUIGCI
GYMNJV
HETDRO
LEPGWA
MONIFC
MYCOLN
MYCOPP
PARZCO
PHAIGR
PHIACI
PHIAGR
PHMPOM
PHYPMA
PHYPPN
PHYPPY
PHYTCN
PHYTFR
PLASHA
PPV000
PSDMAC
PUCCHN
PUCCPT
PUCCPZ
RAFFLA
RALSSL
RRV000
SCIRAC
SCIRPI
SYNCEN
THEKMI
THPHSO
TILLCO
XANTAM
XANTFR
XYLEFA
""".strip().splitlines()
eppo_codes
#%%
# Cycle through codes and download datasheets
for code in eppo_codes:
    url = f"https://gd.eppo.int/taxon/{code}/download/datasheet_doc"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the document
        filename = os.path.join(output_dir, f"{code}.doc")
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {code}: {e}")
#%%
# Convert .doc files to markdown

md_output_dir = "datasheets_md"
os.makedirs(md_output_dir, exist_ok=True)

for code in tqdm(eppo_codes):
    doc_file = os.path.join(output_dir, f"{code}.doc")
    md_file = os.path.join(md_output_dir, f"{code}.md")
    
    try:
        # Use pandoc to convert doc to markdown
        subprocess.run(
            ["pandoc", "-f", "docx", "-t", "markdown", doc_file, "-o", md_file],
            check=True,
            capture_output=True
        )
        print(f"Converted: {md_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {code}: {e}")
    except FileNotFoundError:
        print("Pandoc not found. Install it with: apt-get install pandoc")

