from huggingface_hub import hf_hub_download
import os

REPO_ID = "vectara/open_ragbench"
LOCAL_DIR = "data"

os.makedirs(LOCAL_DIR, exist_ok=True)

files_to_get = [
    "pdf/arxiv/queries.json",
    "pdf/arxiv/qrels.json",
    "pdf/arxiv/answers.json",
]

for f in files_to_get:
    hf_hub_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        filename=f,
        local_dir=LOCAL_DIR,
    )

print("Metadata files downloaded.")