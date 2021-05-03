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
