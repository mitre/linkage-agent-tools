# Linkage Agent Tools Executables
Fork of https://github.com/mitre/linkage-agent-tools. All python files should conform to existing command line documentation. Command line and GUI tools should be interoperable. Executables built using pyinstaller version 4.2. Docker remains a dependency.
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
### GarbleExecutable.py
- WxPython GUI wrapper for functions inside garble.py
- Able to be built into a folder with an executable using pyinstaller
- Currently includes Schema files inside the built folder
- Runs multiprocessing.freeze_support() to enable multiprocessing in the built executable.


## Build Instructions
Clone the repository. From the cloned directory run the following commands:  
`pip install -r requirements.txt`  
`pyinstaller DCCExecutable.py  --add-data anonlink-entity-service;anonlink-entity-service --add-data config.json;.`
