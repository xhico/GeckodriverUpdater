# -*- coding: utf-8 -*-
# !/usr/bin/python3

import os
import json
import random
import shutil
import string
import zipfile
import tarfile
import logging
import requests
import traceback
import urllib.request
from Misc import get911, sendEmail


def unpackFile(file_path, extract_path):
    """
    Extracts files from the specified archive file to the given extraction path.

    Parameters:
    - file_path (str): The path to the archive file.
    - extract_path (str): The path where the contents of the archive should be extracted.

    Raises:
    - Exception: If the file type is not supported.

    """
    # Log the extraction process
    logger.info(f"Extracting {file_path}")

    try:
        # Check the file type and use the appropriate extraction method
        if file_path.endswith(".gz"):
            with tarfile.open(file_path, 'r:gz') as tar:
                tar.extractall(extract_path)
        elif file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        else:
            # Raise an exception for unsupported file types
            raise Exception(f"Unsupported file type")

    except Exception as ex:
        # Log an error message if an exception occurs during extraction
        logger.error(f"Error extracting - {ex}")


def generateRandomString(length):
    """
    Generates a random string of the specified length using ASCII letters and digits.

    Parameters:
    - length (int): The desired length of the random string.

    Returns:
    - str: A randomly generated string.

    """
    # Define the set of characters to use in the random string
    characters = string.ascii_letters + string.digits

    # Generate a random string of the specified length
    randomString = ''.join(random.choice(characters) for _ in range(length))

    # Return the generated random string
    return randomString


def main():
    """
    Downloads the latest Geckodriver JSON, selects the appropriate asset, and extracts it.

    """
    # Log the start of the process
    logger.info(f"Download Geckodriver latest JSON")

    # Get the latest JSON from the Geckodriver GitHub repository
    latestJSON = requests.get("https://api.github.com/repos/mozilla/geckodriver/releases/latest").json()
    assets = [asset for asset in latestJSON.get("assets", []) if "asc" not in asset.get("name", "")]

    # Check if latest version is not newer
    tagName = latestJSON["tag_name"]
    if CONFIG["version"] == tagName:
        logger.info(f"Tag {tagName} already exists")
        return

    # Update Version on CONFIG
    CONFIG["version"] = tagName

    # Create a temporary folder for downloads
    temp_folder = os.path.join(CONFIG["temp_download_folder"], generateRandomString(8))
    os.makedirs(temp_folder, exist_ok=True)

    for asset in assets:
        assetName = asset["name"]
        assetURL = asset["browser_download_url"]

        for configAsset in CONFIG["assets"]:
            if configAsset["name"] in assetName:
                logger.info("--------------------")
                logger.info(f"Name: {assetName}")

                # Generate a random string for temp file and download the asset
                assetRandomString = generateRandomString(8)
                tempAssetURLFile = os.path.join(temp_folder, f"{assetRandomString}.{assetName.split('.')[-1]}")
                urllib.request.urlretrieve(assetURL, tempAssetURLFile)

                # Create a temp folder for extraction
                unpackFolder = os.path.join(temp_folder, assetRandomString)
                unpackFile(tempAssetURLFile, unpackFolder)

                # Get source and target file paths
                sourceGeckodriverFilePath = os.path.join(unpackFolder, os.listdir(unpackFolder)[0])
                targetFilename = configAsset["filename"] if len(CONFIG["assets"]) != 1 else "geckodriver"
                targetGeckodriverFilePath = os.path.join(CONFIG["download_folder"], targetFilename)

                # Log source and target file paths
                logger.info(f"Source Geckodriver: {sourceGeckodriverFilePath}")
                logger.info(f"Target Geckodriver: {targetGeckodriverFilePath}")

                # Rename and clean up
                os.rename(sourceGeckodriverFilePath, targetGeckodriverFilePath)
                os.system(f"chmod +x {targetGeckodriverFilePath}")
                shutil.rmtree(unpackFolder)
                os.remove(tempAssetURLFile)

                # Send email notification
                sendEmail("Geckodriver Update", f"Version {tagName}")

                # Break out of the inner loop as asset is found
                break

    # Clean up the temporary folder
    shutil.rmtree(temp_folder)

    # Save Info to SAVED_INFO_FILE
    with open(CONFIG_FILE, 'w') as outfile:
        json.dump(CONFIG, outfile, indent=2)


if __name__ == '__main__':
    # Set Logging
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{os.path.abspath(__file__).replace('.py', '.log')}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])
    logger = logging.getLogger()

    logger.info("----------------------------------------------------")

    # Open the configuration file in read mode
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(CONFIG_FILE) as inFile:
        CONFIG = json.load(inFile)

    try:
        main()
    except Exception as ex:
        logger.error(traceback.format_exc())
        sendEmail(os.path.basename(__file__), str(traceback.format_exc()))
    finally:
        logger.info("End")
