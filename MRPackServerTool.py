import json
import os
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from zipfile import ZipFile

import wget

# Debug
SKIP_OVERRIDES = True
SKIP_DOWNLOADS = False

root = tk.Tk()
root.withdraw()

print("Welcome to the MRPack Server Tool.\n")

# Ask for source file and destination folder
mrpack_path = filedialog.askopenfilename(
    title="Please select a modpack file.",
    filetypes=[("Modrinth Modpacks", ".mrpack")],
    initialdir=".",
)
destination_folder = filedialog.askdirectory(
    title="Please select the server folder.",
    initialdir=".",
)

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
            required_server_mods = [ mod for mod in index_json["files"] if mod["env"]["server"] == "required" ]
            optional_server_mods = [ mod for mod in index_json["files"] if mod["env"]["server"] == "optional" ]
            num_client_side_mods = len(index_json["files"]) - (len(required_server_mods) + len(optional_server_mods))
            print(f"- Found {len(required_server_mods)} required server mods.")
            print(f"- Found {len(optional_server_mods)} optional server mods.")
            print(f"- Skipping {num_client_side_mods} client-only mods.\n")

            # Download required mods
            # TODO

            # Prompt for and download optional mods
            # TODO
        else:
            print("DEBUG: Skipping downloads...\n")

print("Done!")
