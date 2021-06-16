# Linkage Agent Tools

Tools for the Childhood Obesity Data Initative (CODI) Linkage Agent to use to accept garbled input from data owners / partners, perform matching and generate network IDs. This can also be thought of as Semi-Trusted Third Party (STTP) tools.

These tool facilitate a Privacy Preserving Record Linkage (PPRL) process. They build on the open source [anonlink](https://github.com/data61/anonlink) software package.

## Installation

### anonlink-entity-service

The primary dependency of these tools is on the [anonlink-entity-service](https://anonlink-entity-service.readthedocs.io/en/stable/). This software package provides a web service for accessing [anonlink](https://github.com/data61/anonlink)'s matching capabilites. This software must be installed for the Linkage Agent Tools to work. Install instructions can be found on the [anonlink-entity-service Deployment page](https://anonlink-entity-service.readthedocs.io/en/stable/deployment.html)

### Dependency Overview

Linkage Agent Tools is a set of scripts designed to interact with the previously mentioned anonlink-entity-service. They were created and tested on Python 3.7.4. The tools rely on two libraries: [Requests](https://requests.readthedocs.io/en/master/) and [TinyDB](https://tinydb.readthedocs.io/en/latest/intro.html).

Requests is a library that makes HTTP requests. This is used for the tools to communicate with the web service offered by the anonlink-entity-service.

TinyDB is a Python-based implementation of a document database. It runs inside of the Python interpreter and stores it's information in a JSON file. TinyDB is used to keep track of matches across anonlink projects. It is then queries to deconflict results between projects and construct a full set of LINK_IDs for all individuals.

Linkage Agent Tools contains a test suite, which was created using [pytest](https://docs.pytest.org/en/latest/).

### Installing with an existing Python install

1. Download the tools as a zip file using the "Clone or download" button on GitHub.
1. Unzip the file.
1. From the unzipped directory run:

    `pip install -r requirements.txt`

### Installing with Anaconda

1. Install Anaconda by following the [install instructions](https://docs.anaconda.com/anaconda/install/).
    1. Depending on user account permissions, Anaconda may not install the latest version or may not be available to all users. If that is the case, try running `conda update -n base -c defaults conda`
1. Download the tools as a zip file using the "Clone or download" button on GitHub.
1. Unzip the file.
1. Open an Anaconda Powershell Prompt
1. Go to the unzipped directory
1. Run the following commands:
    1. `conda create --name codi`
    1. `conda activate codi`
    1. `conda install pip`
    1. `pip install -r requirements.txt`

## Configuration

Linkage Agent Tools is driven by a central configuration file, which is a JSON document. An example is shown below:

```
{
  "systems": ["a", "b", "c"],
  "projects": ["name-sex-dob-phone", "name-sex-dob-zip",
    "name-sex-dob-parents", "name-sex-dob-addr"],
  "schema_folder": "/path/to/schema",
  "inbox_folder": "/path/to/inbox",
  "matching_results_folder": "/path/to/results",
  "output_folder": "/path/to/output",
  "entity_service_url": "http://localhost:8851/api/v1",
  "matching_threshold": 0.8
}
```
A description of the properties in the file:
* **systems** - The set of data owners in this matching effort. These are short names for the participants. When data owners send zip files, it is expected that they will have the format of "data owner name".zip.
* **projects** - The anonlink [linkage projects](https://anonlink-entity-service.readthedocs.io/en/stable/tutorial/Record%20Linkage%20API.html#Create-Linkage-Project) that are going to be used in this matching effort. It assumes that the project names will have a corresponding anonlink schema file in the schema folder.
* **schema_folder** - A folder containing [anonlink schema files](https://clkhash.readthedocs.io/en/latest/schema.html). The schema files should be named "project name".json.
* **inbox_folder** - The folder where zip files recieved from data owners should be placed.
* **matching_results_folder** - Folder where the CSV containing the complete mapping of LINK_IDs to all data owners
* **output_folder** - Folder where CSV files are generated, one per data owner. These files contain LINK_IDs mapped to a single data owner.
* **entity_service_url** - The RESTful service endpoint for the anonlink-entity-service.
* **matching_threshold** - The threshold for considering a potential set of records a match when comparing in anonlink.

## Structure

This project is a set of python scripts driven by a central configuration file, `config.json`. It is expected to operate in the following order:

1. Data owners transmit their garbled zip files to the Linkage Agent. These zip files should be placed into the configured inbox folder.
1. Run `validate.py` which will ensure all of the necessary files are present.
1. When all data is present, run `match.py`, which will perform pairwise matching of the garbled information sent by the data owners. The matching information will be stored in a JSON file created by TinyDB.
1. After matching, run `linkids.py`, which will take all of the resulting matching information and use it to generate LINK_IDs, which are written to a CSV file in the configured results folder.
1. Once all LINK_IDs have been created, run `dataownerids.py` which will create a file per data owner that can be sent with only information on their LINK_IDs.

## Clean Up

Running `match.py` creates a file called `results.json` that is storage for TinyDB. This file should be removed between matching runs, otherwise the matching runs will be combined. Running `python linkids.py --remove` will remove this file once the LINKIDs have been generated.

## Running Tests

Linkage Agent Tools contains a unit test suite. Tests can be run with the following command:

`python -m pytest`

# Linkage Agent Tools Executables
Fork of https://github.com/mitre/linkage-agent-tools. All python files should conform to existing command line documentation. Command line and GUI tools should be interoperable. Executables built using pyinstaller version 4.2. Docker remains a dependency.

## Basic User Instructions
Download the DCCexecutable.zip file from https://github.com/Sam-Gresh/linkage-agent-tools/releases/tag/v0.0.3. Unzip the file to a new directory. In the folder DCCExecutable, run the executable DCCexecutable and select the correct schema, inbox, and output directories. If an error occurs, the directories can be set manually from config.json. Make sure docker is running, then click start service. Place the garbled zip files in the specified inbox directory, and set the "Data providers" field. Validate the inbox, then click Match. All csv outputs should appear in the specified output directory after some time.

## Change Log
### match.py
- Moved majority of code into callable function

### validate.py
- Moved majority of code into callable function
- Moved argparse code into \_\_name\_\_ == "\_\_main\_\_" check
- Function returns messages instead of printing

### linkids.py
- Moved majority of code into callable function
- Moved argparse code into \_\_name\_\_ == "\_\_main\_\_" check
- Function returns messages instead of printing

## Additions
### DCCExecutable.py
- WxPython GUI wrapper for functions listed above
- Able to be built into a one-folder executable using pyinstaller
- Currently does not include Schema files inside the built folder
- Runs multiprocessing.freeze_support() to enable multiprocessing in the built executable.


## Build Instructions
Clone the repository. From the cloned directory run the following commands:  
`pip install -r requirements.txt`  
`pyinstaller DCCExecutable.py  --add-data anonlink-entity-service;anonlink-entity-service --add-data config.json;.`

The built executable will appear in /dist.

## Notice

Copyright 2020 The MITRE Corporation.

Approved for Public Release; Distribution Unlimited. Case Number 19-2008
