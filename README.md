# tox-lambda-autodiscovery

[![PyPI version](https://img.shields.io/pypi/v/tox-lambda-autodiscovery.svg)](https://pypi.org/project/tox-lambda-autodiscovery)
[![Python versions](https://img.shields.io/pypi/pyversions/tox-lambda-autodiscovery.svg)](https://pypi.org/project/tox-lambda-autodiscovery)
[![See Build Status on Travis CI](https://travis-ci.com/luzfcb/tox-lambda-autodiscovery.svg?branch=master)](https://travis-ci.com/luzfcb/tox-lambda-autodiscovery)
[![See Build Status on AppVeyor](https://ci.appveyor.com/api/projects/status/github/luzfcb/tox-lambda-autodiscovery?branch=master)](https://ci.appveyor.com/project/luzfcb/tox-lambda-autodiscovery/branch/master)
[![Coverage 
Status](https://coveralls.io/repos/github/luzfcb/tox-lambda-autodiscovery/badge.svg)](https://coveralls.io/github/luzfcb/tox-lambda-autodiscovery)

Autodiscovery and autocreate tox testenv to aws lambda functions

------------------------------------------------------------------------

This [Pytest](https://github.com/pytest-dev/pytest) plugin was generated
with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with
[\@obestwalter](https://github.com/obestwalter)\'s
[Cookiecutter-tox-plugin](https://github.com/tox-dev/cookiecutter-tox-plugin)
template.


### This project is not yet ready for production.


## Features

Autodiscovery and autocreate tox testenv to aws lambda function.

TODO:
- [ ] rewrite code when tox api is more flexible: https://mail.python.org/mm3/archives/list/tox-dev@python.org/thread/2B2GXTFWCE6FYMVCMBMKAOQAXEOGXEWR/
- [ ] Write tests

## Requirements

- Python >= 3.6, tox >= 3.3.0

## Installation

You can install `tox-lambda-autodiscovery` via [pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org):

```
$ pip install tox-lambda-autodiscovery
```
    
or directly from github:

```
$ pip install -e git+https://github.com/luzfcb/tox-lambda-autodiscovery@master#egg=tox-lambda-autodiscovery
```

## Usage

Add a new section named `[testenv:lambdaautodiscovery]` on `tox.ini`.

> The plugin is active only when the section `[testenv:lambdaautodiscovery]` exists.


### Configuration options for `[testenv:lambdaautodiscovery]`

#### `search_dirs`

A list of directories that the plugin uses as autodiscover. _The default value is `{toxinidir}`_.

##### Example

Having a list of directories, with subdirectories, which contains a file `requirements.txt`, and a python file started with `test` on the same directory level:

```
project:
       README.md
       backend1/
              serverless.yml
              package.json
              node_modules/
              functionCreateRole/
                   create_role.py
                   requirements.txt
                   test_create_role.py
       backend2/
              serverless.yml
              package.json
              node_modules/
              functionCreateUser/
                   create_user.py
                   requirements.txt
                   test_create_user.py
```

The `search_base_dirs` looks like the following:

```ini
search_dirs = backend1
              backend2
```

#### `ignored_dirs`

Directories that the plugin should ignore in autodiscovery.

##### Example

```
ignored_dirs = .serverless
               .vscode
```

The directories with the following names are ignored by default:

```
.tox
__pycache__
eggs/
.eggs/
node_modules
```

> If you want to override the default ignored directories names, use the option `default_ignored_dir_names`.


the `commands_workaround` is a way to customize tox `commands`

eg.:

```
commands_workaround = {posargs:pytest} --cov={current_toxenv_lambda_dir} --basetemp={envtmpdir}
```

> is ugly, but, tox 3.3.0 api has no simple way to defer processing of `commands`


The `PYTHONPATH` can be customized by setting

```
setenv =
    PYTHONPATH = {toxinidir}/backend/
```

### Full sample config:

the following directories structure:

```
(myproject) fabio@luzfcb:~/projects$ tree myproject -L 2
myproject
├── README.md
├── backend
│   ├── README.md
│   ├── .serverless
│   │     ├── serverless-state.json
│   │     ├── cloudformation-template-create-stack.json
│   │     ├── functionOne
│   │     │     ├── requirements
│   │     │     └── requirements.txt
│   │     ├── functionTwo
│   │     │     ├── requirements
│   │     │     └── requirements.txt
│   ├── functionOne
│   │     ├── function_one.py
│   │     ├── test_function_one.py 
│   │     └── requirements.txt
│   ├── functionTwo
│   │     ├── function_two.py
│   │     ├── test_function_two.py 
│   │     └── requirements.txt
│   ├── apps
│   │     └── configure_django
│   │     │     └── __init__.py
│   │     └── myapp
│   │           ├── __init__.py
│   │           ├── apps.py
│   │           ├── models.py
│   │           └── migrations
│   └── serverless.yml
├── buildspec.yaml
├── cloudformation
│   └── dev-resources.yaml
├── codecov.yml
├── requirements.txt
├── requirements_dev.txt
├── setup.cfg
├── testspec.yaml
└── tox.ini
```


The configuration:

```
[testenv:lambdaautodiscovery]
commands_workaround = {posargs:pytest} --cov-append --cov={current_toxenv_lambda_dir} --basetemp={envtmpdir}

ignored_dirs = .serverless

search_dirs = backend

setenv =
    PYTHONPATH = {toxinidir}/backend/apps

```

## Contributing

Contributions are very welcome. Tests can be run with [tox](https://tox.readthedocs.io/en/latest/), please ensure the coverage at least stays the same before you submit a pull request.


## License

Distributed under the terms of the [MIT](http://opensource.org/licenses/MIT) license, `tox-lambda-autodiscovery` is free and open source software.


## Issues

If you encounter any problems, please [file an issue](https://github.com/luzfcb/tox-lambda-autodiscovery/issues) along with a detailed description.
