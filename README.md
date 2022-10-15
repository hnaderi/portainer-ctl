### Portainer bot

#### Features
- Fully automated deployment
- Support for multiple config and secret
- Support for .env files and multiple variables
- Support for api tokens introduced in portainer 2.11.0

#### Usage

``` plaintext
usage: pctl [-h] [-T API_TOKEN] [-H HOST] [-U USERNAME] [-P PASSWORD] {deploy,destroy} ...

Portainer deployment client

optional arguments:
  -h, --help            show this help message and exit
  -T API_TOKEN, --api-token API_TOKEN
                        api token for user, overrides PORTAINER_TOKEN variable
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
- PORTAINER_TOKEN

##### deploy command

``` plaintext
usage: pctl deploy [-h] -f COMPOSE_FILE -n NAME -E {staging,production}
                   [-S STACK_NAME] [--env-file ENV_FILE] [-e VARIABLE]
                   [-c CONFIG] [-s SECRET]

options:
  -h, --help            show this help message and exit
  -f COMPOSE_FILE, --compose-file COMPOSE_FILE
                        compose manifest file
  -n NAME, --name NAME  deployment name
  -E {staging,production}, --environment {staging,production}
                        environment to deploy on
  -S STACK_NAME, --stack-name STACK_NAME
                        use this to override stack name
  --env-file ENV_FILE   dot env file used for deployment, it will be used as
                        stack environment in portainer
  -e VARIABLE, --variable VARIABLE
                        environment variable `SOME_ENV=some-value`
  -c CONFIG, --config CONFIG
                        create config; args must be like `local-path-to-
                        file:conf-name`; NOTE that as configs are immutable
                        and might be already in use, your config name must not
                        exist! use versioning or date in names to always get a
                        new name
  -s SECRET, --secret SECRET
                        create a new secret; see --config.
```
