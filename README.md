# Style Transfer Framework

Presented by IVision

## Demo

- PC Browser: https://ivision.vlionthu.com:2443
- Phone: http://ivision.vlionthu.com:2080/mobile

![QR Code for Mobile Clients](images/qr.jpg)

## Screenshot

![Screenshot of Desktop Client](images/screenshot_desktop.png)

![Screenshot of Mobile Client](images/screenshot_mobile.png)

## How to run this

### Auto Deploy From Your Client Computer

We have implemented an auto deploy tool based on [fabric](http://www.fabfile.org). Cd to `/tornado-supported-webapp`, create a server configuration file `Backend/configs/server.yml`

```yaml
user: username-of-server
domain_or_ip: server_addr
port: 22
project_root: /path/to/project_root
```

Make sure you have required permission for `project_root` directory.  After that run `fab deploy` from terminal. Then the project will be uploaded to your server and all the running scripts will be generated correctly. 

### Manual Setup on Server

You can manually download the project into your server, and make the necessary configuration by hand. 

First clone the project into your server, and create a virtual environment  of python3. The `requrements.txt` file is located at `tornado-supported-webapp/Backend/requrements.txt`. 

Second, cd to `tornado-supported-webapp/Backend/configs`, and run `process.py` file. This script accepts two arguments: `--user`  to set the user to run the project, and `--gpu_num` to set the number of GPU to use. 

> You can get the number of GPUs available by running `nvidia-smi -L | wc -l`. 

Two configuration file will be generated automatically: `supervisor.conf` and `nginx.conf`. You can you `supervisor.conf` directly. However, further modification should be made to `nginx.conf`. Open this file using your favorite editor, and change `server_name` to your own domain name. 

Last, you need to modify `tornado-supported-webapp/Backend/run.sh`

```bash
#!/usr/bin/env bash
/home/huangy/style-transfer/env/bin/python3 /home/huangy/style-transfer/style-transfer/tornado-supported-webapp/Backend/start.py --cuda=true "$@"
```

change the path to the executable python3 file and the path to start.py to correct value, and make this file executable by

```bash
chmod u+x tornado-supported-webapp/Backend/run.sh
```

### About SSL Certificate

You need to put your SSL Certificate file at ``tornado-supported-webapp/Backend/configs/Certificates`  and name them `domain.crt` and `domain.key` respectively.

