#! /usr/bin/env kpython3

"""
This script is the primary entry point to the translator module from the command line.
It does three important things:
1. It adds the base translator module to the PYTHONPATH, which is needed to access `cli_interface.py`
2. It adds the translator for a specific instrument to PYTHONPATH, which is needed to import it
3. It calls `main` on `cli_interface` with the appropriate arguments
"""

import sys

# 

# Where is ddoiserver?
# server_location = '/net/vm-ddoiserverbuild'
server_location = "" # When running on a ddoiserver, this should be set to none (unless /net is set up)

# Where is the translator module, starting from the root directory of the server?
translator_module_location = "/ddoi/KPFTranslator/default/KPFTranslator"

# Where is the linking table?
linking_table_location = f"{server_location}{'/' if server_location else ''}{translator_module_location}/kpf/linking_table.yml"


# Add the cli script to import path
sys.path.insert(0, f"{server_location}/ddoi/DDOITranslatorModule/default/DDOITranslatorModule")
import ddoitranslatormodule.cli_interface as cli

# Add the translator module to the python path
sys.path.insert(0, f"{server_location}/{translator_module_location}")

# Call main with the linking table location and arguments
cli.main(linking_table_location, sys.argv[1:])
