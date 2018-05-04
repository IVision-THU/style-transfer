#!/usr/bin/env python3
import os
import argparse

CONFIG_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)

parser = argparse.ArgumentParser(description="Preprocess configuration files for deployment")
parser.add_argument(
    "--gpu_num", dest="gpu_num", default=0,
    type=int, help="number of GPUs")
parser.add_argument(
    "--user", dest="user", default="woody",
    type=str, help="user to run project"
)


def fill_project_root(template_file_path, output_file_path):
    template_file = open(os.path.join(CONFIG_DIR, template_file_path))
    config_file = open(os.path.join(CONFIG_DIR, output_file_path), "w")
    config_file.write(
        template_file.read().replace("||Project_Root||", BASE_DIR)
    )
    config_file.close()
    template_file.close()


def set_nginx_upstream_numbers(filepath, gpu_num):
    with open(filepath, "r+") as f:
        content = f.read()
        config_content = "\n".join(["\t\tserver 127.0.0.1:80%02d" % x for x in range(gpu_num)])
        f.seek(0)
        f.write(content.replace("||UPSTREAMS||", config_content))
        f.truncate()


def set_supervisor_config_file(filepath, user, gpu_num):
    with open(filepath, "r+") as f:
        content = f.read()
        f.seek(0)
        f.write(content.replace("||USER||", user).replace("||GPU_NUM||", str(gpu_num)))
        f.truncate()


if __name__ == "__main__":
    args = parser.parse_args()
    gpu_num = min(args.gpu_num, 4)
    user = args.user
    fill_project_root("supervisor_template.conf", "supervisor.conf")
    fill_project_root("nginx_template.conf", "nginx.conf")
    set_nginx_upstream_numbers("nginx.conf", gpu_num)
    set_supervisor_config_file("supervisor.conf", user, gpu_num)

