import hashlib
import json
import os
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Dict
from zipfile import ZipFile

import requests

# Debug
SKIP_OVERRIDES = False
SKIP_DOWNLOADS = False
# Other constants
REQUEST_HEADERS = {"User-Agent": "lyao6104/MRPackServerTool/0.1.1"}
HASH_ALGORITHMS = {
    "sha1",
    "sha512",
}


def download(url: str, destination: str, hashes: Dict[str, str]):
    # Send request
    response = requests.get(url=url, headers=REQUEST_HEADERS)

    # Verify hashes
    for algorithm in HASH_ALGORITHMS:
        hash_func = getattr(hashlib, algorithm)
        assert hash_func(response.content).hexdigest() == hashes.get(
            algorithm
        ), f"{algorithm} hash for downloaded file does not match expected value."

    # Save file
    with open(destination, "wb") as file:
        file.write(response.content)


root = tk.Tk()
root.withdraw()

print()

print("Welcome to the MRPack Server Tool.\n")

# Ask for source file and destination folder
mrpack_path = filedialog.askopenfilename(
    title="Please select a modpack file.",
    filetypes=[("Modrinth Modpacks", ".mrpack")],
    initialdir=".",
)
if not mrpack_path:
    print("No modpack selected, exiting...")
    exit()
destination_folder = filedialog.askdirectory(
    title="Please select the server folder.",
    initialdir=".",
)
if not destination_folder:
    print("No server folder selected, exiting...")
    exit()

with ZipFile(mrpack_path) as mrpack:
    with mrpack.open("modrinth.index.json") as index_file:
        # Load index and output name + version
        index_json = json.loads(index_file.read())
        print(f"Loaded {index_json['name']} {index_json['versionId']}.\n")

        # Overrides
        if not SKIP_OVERRIDES:
            print("Copying server overrides...")
            overrides = list(
                filter(
                    lambda name: "overrides/" in name,
                    mrpack.namelist(),
                )
            )
            temp_overrides_path = f"./Temp/{index_json['name']}/"
            os.makedirs(temp_overrides_path)
            mrpack.extractall(temp_overrides_path, overrides)
            for child in Path(f"{temp_overrides_path}/overrides").iterdir():
                # print(child)
                print(f"- Copying {child.name} folder...")
                destination_path = f"{destination_folder}/{child.name}/"
                # print(destination_path)
                shutil.copytree(child, destination_path, dirs_exist_ok=True)
            shutil.rmtree("./Temp")
            print("Done copying overrides.\n")
        else:
            print("DEBUG: Skipping overrides...\n")

        # Install server mods
        if not SKIP_DOWNLOADS:
            # Display some information
            print("Searching for server-side mods...")
            required_server_mods = [
                mod for mod in index_json["files"] if mod["env"]["server"] == "required"
            ]
            optional_server_mods = [
                mod for mod in index_json["files"] if mod["env"]["server"] == "optional"
            ]
            num_client_side_mods = len(index_json["files"]) - (
                len(required_server_mods) + len(optional_server_mods)
            )
            print(f"- Found {len(required_server_mods)} required server mods.")
            print(f"- Found {len(optional_server_mods)} optional server mods.")
            print(f"- Skipping {num_client_side_mods} client-only mods.\n")

            # Download required mods
            print("Downloading required mods...")
            for mod in required_server_mods:
                mod_name = mod["path"].replace("mods/", "", 1)
                print(f"- Attempting download for {mod_name}...")
                download(
                    mod["downloads"][0],
                    f"{destination_folder}/{mod['path']}",
                    mod["hashes"],
                )
                print(f"  - Download successful")
            print("Finished downloading required mods.\n")

            # Prompt for and download optional mods
            print("Downloading optional mods...")
            for mod in optional_server_mods:
                mod_name = mod["path"].replace("mods/", "", 1)
                user_response = input(f"- Download optional mod {mod_name} (Y/n)? ")
                if user_response == "n":
                    print("  - Skipping...")
                    continue
                else:
                    print(f"  - Attempting download for {mod_name}...")
                    download(
                        mod["downloads"][0],
                        f"{destination_folder}/{mod['path']}",
                        mod["hashes"],
                    )
                    print(f"  - Download successful")
            print("Finished downloading optional mods.\n")
        else:
            print("DEBUG: Skipping downloads...\n")

print("Done!")
