# GeckodriverUpdater

Downloads the latest Geckodriver JSON, selects the appropriate asset, and extracts it.

## Config

Loads config from local file (Example bellow)

```
{
  "version": "v0.34.0",
  "temp_download_folder": "/tmp/",
  "download_folder": "/Downloads/",
  "assets": [
    {
      "name": "linux32",
      "filename": "geckodriver_armf"
    },
    {
      "name": "linux-aarch64",
      "filename": "geckodriver_arm64"
    },
    {
      "name": "macos-aarch64",
      "filename": "geckodriver_mac"
    },
    {
      "name": "win-aarch64",
      "filename": "geckodriver_win"
    }
  ]
}
```

## Installation

```
python3 -m pip install -r requirements.txt --no-cache-dir
```

## Usage

Manual

```
python3 GeckodriverUpdater.py
```
