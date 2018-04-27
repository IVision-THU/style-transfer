import os
import yaml

from fabric.api import env, cd, run
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


def _load_server_settings():
    server_settings = {}
    local_server_config_path = os.path.join(BASE_DIR, "Backend", "configs", "servers.yml")
    if os.path.exists(local_server_config_path):
        server_config = yaml.load(open(local_server_config_path))
        env.hosts = ["{user}@{domain_or_ip}:{port}".format(
            user=server_config["user"],
            domain_or_ip=server_config["domain_or_ip"],
            port=server_config.get("port", "22")
        )]
        if "password" in server_config:
            env.password = server_config["password"]
        server_settings["project_root"] = server_config["project_root"]
        server_settings["env_root"] = server_config.get("env_root", None)
        server_settings["backend_proj_root"] = os.path.join(
            server_settings["project_root"], "style-transfer/tornado-supported-webapp/Backend")
        server_settings["frontend_proj_root"] = os.path.join(
            server_settings["project_root"], "style-transfer/tornado-supported-webapp/Frontend")
        return server_settings
    else:
        print("%s not found" % local_server_config_path)
        return None


def _locate_or_create_python_virtualenv(settings):
    env_root = settings.get("env_root")
    project_root = settings["project_root"]
    backend_proj_root = settings["backend_proj_root"]
    if env_root is None:
        with cd(project_root):
            if not exists("env"):
                run("virtualenv -p python3 env")
                requirements_file = os.path.join(
                    backend_proj_root, "requirements.txt"
                )
                run("env/bin/pip install -r {} > /dev/null".format(
                    requirements_file
                ))
            env_root = os.path.join(project_root, "env")
            settings["env_root"] = env_root
    else:
        if not exists(env_root) or \
                not exists(os.path.join(env_root, "bin/activate")):
            print("Invalid python env at %s" % env_root)
            return None
    return env_root


def _create_env_link_for_model_tools(settings, env_root):
    python_lib = os.path.join(env_root, "lib/")
    project_root = settings["project_root"]
    with cd(python_lib):
        python_dir = run("ls -1 | head -1")
        target_link = os.path.join(
            python_lib, python_dir, "site-packages/style_transfer_tools")
        if not exists(target_link):
            run("ln -s {} {}".format(
                os.path.join(
                    project_root, "style-transfer/pytorch_fast-neural-style/neural_style"),
                target_link))


settings = _load_server_settings()


def _process_configs_files(settings, env_root):
    backend_root = settings["backend_proj_root"]
    with cd(os.path.join(backend_root, "configs")):
        run("chmod u+x ./process.py && ./process.py")


def deploy():
    if settings is None:
        return
    project_root = settings["project_root"]

    if not exists(project_root):
        run("mkdir -p %s" % project_root)
    rsync_project(local_dir=os.path.join(ROOT_DIR), remote_dir=project_root,
                  exclude=[".git", ".idea", "env", ".DS_store", "*.pyc", "venv"])
    env_root = _locate_or_create_python_virtualenv(settings)
    if env_root is None:
        return
    _create_env_link_for_model_tools(settings, env_root)
    _process_configs_files(settings, env_root)
    with cd(settings["backend_proj_root"]):
        run("chmod u+x ./run.sh")
        run("./run.sh")
