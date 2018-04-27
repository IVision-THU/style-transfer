#!/usr/bin/env python3
import os

CONFIG_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)


def fill_project_root(template_file_path, output_file_path):
    template_file = open(os.path.join(CONFIG_DIR, template_file_path))
    config_file = open(os.path.join(CONFIG_DIR, output_file_path), "w")
    config_file.write(
        template_file.read().replace("||Project_Root||", BASE_DIR)
    )
    config_file.close()
    template_file.close()


if __name__ == "__main__":
    fill_project_root("supervisor_template.conf", "supervisor.conf")
    fill_project_root("nginx_template.conf", "nginx.conf")
