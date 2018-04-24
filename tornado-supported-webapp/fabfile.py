import os
import yaml

from fabric.api import env, cd, run
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
project_root = None
env_root = None
python_version = None


def _load_server_settings():
    global project_root
    global env_root
    global python_version
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
        env_root = server_config.get("env_root", None)
        python_version = server_config.get("python_version", "3.6")
    else:
        print("%s not found" % server_config_path)
        return []


_load_server_settings()


def deploy():
    global project_root
    global env_root
    global python_version
    if project_root is None:
        print("invalid project root")
        return
    if not exists(project_root):
        run("mkdir %s" % project_root)
    rsync_project(local_dir=os.path.join(ROOT_DIR), remote_dir=project_root,
                  exclude=[".git", ".idea", "env", "DS_store"])
    if env_root is not None:
        target_link = os.path.join(env_root, "lib/python%s" % python_version,
                                   "site-packages/style_transfer_tools")
        if not exists(target_link):
            run("ln -s {} {}".format(
                os.path.join(project_root,
                             "style-transfer/pytorch_fast-neural-style/neural_style"),
                target_link
            ))
    project_root = os.path.join(project_root, "style-transfer/tornado-supported-webapp/Backend")
    with cd(project_root):
        run("chmod u+x ./run.sh")
        run("./run.sh")
