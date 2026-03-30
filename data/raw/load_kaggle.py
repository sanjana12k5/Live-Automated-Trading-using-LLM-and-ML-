import kagglehub
import os
import shutil

def download_dataset():
    source_path = kagglehub.dataset_download("camnugent/sandp500")
    target_path = "data/raw/sandp500"

    os.makedirs(target_path, exist_ok=True)

    for root, dirs, files in os.walk(source_path):
        for file in files:
            if file.endswith(".csv"):
                src = os.path.join(root, file)
                dst = os.path.join(target_path, file)
                shutil.copy(src, dst)

    print("Dataset copied successfully to:", target_path)

if __name__ == "__main__":
    download_dataset()
