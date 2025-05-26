### Portainer controller
[![](https://img.shields.io/pypi/v/portainer-ctl)](https://pypi.org/project/portainer-ctl/)

### Install
This project is published to PyPi and you can install it using pip:
```
pip install portainer-ctl
```

You can also use the published container images:

```sh
docker pull hnaderi/pctl
# or
docker pull ghcr.io/hnaderi/pctl
```

#### Features
- Fully automated deployment
- Support for multiple config and secret
- Support for .env files and multiple variables
- Support for api tokens introduced in portainer 2.11.0

#### Usage

``` plaintext
Usage: pctl [-h] [-T API_TOKEN] [-H HOST] [-U USERNAME] [-P PASSWORD] [--debug] [-j] {deploy,stacks,configs,secrets,endpoints,tags,system} ...

Poorman's kubectl, CLI for portainer on docker swarm

Options:
  -h, --help            show this help message and exit
  -T, --api-token API_TOKEN
                        api token for user, overrides PORTAINER_TOKEN variable (default: None)
  -H, --host HOST       portainer host, overrides PORTAINER_HOST variable (default: http://127.0.0.1:9000/api)
  -U, --username USERNAME
                        username to login, overrides PORTAINER_USERNAME variable (default: admin)
  -P, --password PASSWORD
                        password for user, overrides PORTAINER_PASSWORD variable (default: admin)
  --debug               Whether or not print debugging logs (default: False)
  -j, --json            Print json output (default: False)

Commands:
  {deploy,stacks,configs,secrets,endpoints,tags,system}

No budget. No vendors. No fleet of ops. Just you, a blinking cursor, and the will to script what others buy. The rich scale with dollars. You scale with shell. Excuses cost, Automation pays!
```

You can provide host, username and password in environment:
- PORTAINER_HOST
- PORTAINER_USERNAME
- PORTAINER_PASSWORD
- PORTAINER_TOKEN
