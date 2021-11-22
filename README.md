### Portainer bot

#### Features
- Fully automated deployment
- Support for multiple config and secret
- Support for .env files and multiple variables

#### Usage

``` plaintext
usage: pctl [-h] [-H HOST] [-U USERNAME] [-P PASSWORD] {deploy,destroy} ...

Portainer deployment client

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  portainer host, overrides PORTAINER_HOST variable; defaults to `http://localhost`
  -U USERNAME, --username USERNAME
                        username to login, overrides PORTAINER_USERNAME variable; defaults to `admin`
  -P PASSWORD, --password PASSWORD
                        password for user, overrides PORTAINER_PASSWORD variable; defaults to admin

subcommands:
  valid subcommands

  {deploy,destroy}      additional help

Use it to automate workflows for less mouse clicks!

```

You can provide host, username and password in environment:
- PORTAINER_HOST
- PORTAINER_USERNAME
- PORTAINER_PASSWORD
