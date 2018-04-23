import os
import yaml

from fabric.api import env, cd, run
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
project_root = None


def _load_server_settings():
    global project_root
    server_config_path = os.path.join(BASE_DIR, "Backend", "configs", "servers.yml")
    if os.path.exists(server_config_path):
        server_config = yaml.load(open(server_config_path))
        env.hosts = ["{user}@{domain_or_ip}:{port}".format(
            user=server_config["user"],
            domain_or_ip=server_config["domain_or_ip"],
            port=server_config.get("port", "22")
        )]
        if "password" in server_config:
            env.password = server_config["password"]
        project_root = server_config["project_root"]
    else:
        print("%s not found" % server_config_path)
        return []


_load_server_settings()


def deploy():
    global project_root
    if project_root is None:
        print("invalid project root")
        return
    if not exists(project_root):
        run("mkdir %s" % project_root)
    rsync_project(local_dir=os.path.join(BASE_DIR, "Backend"), remote_dir=project_root)
    project_root = os.path.join(project_root, "Backend")
    with cd(project_root):
        run("chmod u+x ./run.sh")
        run("./run.sh")
