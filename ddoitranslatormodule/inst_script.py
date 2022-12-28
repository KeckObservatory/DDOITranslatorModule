import sys

server_location = '/net/vm-ddoiserverbuild'
translator_module_location = "/ddoi/KPFTranslator/default/KPFTranslator"
linking_table_location = f"{server_location}/{translator_module_location}/kpf/linking_table.yml"


# Add the cli script to impport path
sys.path.insert(0, f"{server_location}/ddoi/DDOITranslatorModule/default/DDOITranslatorModule")
import ddoitranslatormodule.cli_interface as cli

# Add the translator module to the python path
sys.path.insert(0, f"{server_location}/{translator_module_location}")

cli.main(linking_table_location, sys.argv[1:])
