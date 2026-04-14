#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import yaml


def replace_string_in_files(replace_string, config_file_path="./dev/set_version_config.yml"):
    # YAML-Datei lesen
    with open(config_file_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)

    # Aus der YAML-Datei den Suchstring und die Dateiliste extrahieren
    search_string = config['version']
    file_list = config['files']
    log_file_path = config.get('log_file', './dev/set_version.log')

    # Dateien durchgehen und den Text ersetzen
    for file_path in file_list:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            content = content.replace(search_string, replace_string)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Replaced in {file_path}")
        except FileNotFoundError:
            print(f"FileNotFoundError: {file_path}")
        except Exception as e:
            print(f"Error during editing {file_path}: {e}")

    # Log-Datei aktualisieren
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(f"Replaced: {search_string} with {replace_string}\n")

    # YAML-Konfigurationsdatei mit neuer Version aktualisieren
    config['version'] = replace_string
    with open(config_file_path, 'w', encoding='utf-8') as config_file:
        yaml.dump(config, config_file)


if __name__ == "__main__":
    input_replace_string = sys.argv[1]
    replace_string_in_files(input_replace_string)
