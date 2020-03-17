# DCC Tools

Tools for a Data Coordinating Center (DCC) to use to accept garbled input from data owners / partners, perform matching and generate network IDs. This can also be thought of as Semi-Trusted Third Party (STTP) tools.

## Structure

This project is a set of python scripts driven by a central configuration file. It is expected to operate in the following order:

1. Data owners transmit their garbled zip files to the DCC
1. TODO - The DCC will use the import_garbled_zip.py script to validate the structure of the zip file and copy the hashes into the inbox folder specified in the config file
1. When all data owners have provided their data, the DCC will run match.py, which will perform pairwise matching of the garbled information sent by the data owners
1. After matching the DCC will run load_networkid_db.py, which will take all of the resulting matching information and load it into a database that is used to generate network IDs.
1. Then execute networkids.py to query the database and build a set of network IDs.
1. exportall.py will then create a CSV file containing a mapping of the entire network
1. TODO create a script to generate a file that can be sent back to individual data owners

## Running Tests

`python3 -m pytest`