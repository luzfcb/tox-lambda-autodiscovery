#tox-lambda-autodiscovery


[![PyPI version](https://img.shields.io/pypi/v/tox-lambda-autodiscovery.svg)](https://pypi.org/project/tox-lambda-autodiscovery)

[![Python versions](https://img.shields.io/pypi/pyversions/tox-lambda-autodiscovery.svg)](https://pypi.org/project/tox-lambda-autodiscovery)

[![See Build Status on Travis CI](https://travis-ci.com/luzfcb/tox-lambda-autodiscovery.svg?branch=master)](https://travis-ci.com/luzfcb/tox-lambda-autodiscovery)

[![See Build Status on AppVeyor](https://ci.appveyor.com/api/projects/status/github/luzfcb/tox-lambda-autodiscovery?branch=master)](https://ci.appveyor.com/project/luzfcb/tox-lambda-autodiscovery/branch/master)

autodiscovery and autocreate tox testenv to aws lambda functions

------------------------------------------------------------------------

This [Pytest](https://github.com/pytest-dev/pytest) plugin was generated
with [Cookiecutter](https://github.com/audreyr/cookiecutter) along with
[\@obestwalter](https://github.com/obestwalter)\'s
[Cookiecutter-tox-plugin](https://github.com/tox-dev/cookiecutter-tox-plugin)
template.



### This project is not yet ready for production.

## Features


-   autodiscovery and autocreate tox testenv to aws lambda function.


TODO:
  - find way to create a new `{current_lambdadir}`, `current_envname` to customize `command`
  ```
  commands =
    {posargs:pytest} --cov={current_lambdadir} --basetemp={envtmpdir}
  ```
  - Write tests

## Requirements

-   Python >= 3.6, tox >= 3.3.0

## Installation


You can install \"tox-lambda-autodiscovery\" via
[pip](https://pypi.org/project/pip/) from [PyPI](https://pypi.org):

    $ pip install tox-lambda-autodiscovery
    
or directly from github:

    $ pip install -e git+https://github.com/luzfcb/tox-lambda-autodiscovery@master#egg=tox-lambda-autodiscovery

## Usage


add a new section named `[testenv:lambdaautodiscovery]` on `tox.ini`

The plugin only is active when this section `[testenv:lambdaautodiscovery]` exist


Configuration options of `[testenv:lambdaautodiscovery]`:

`search_base_dirs`: a list of directories that plugin use as autodiscover
Default value is `{toxinidir}`

example:

having a list of directories, with subdirectories, which contains a file `requirements.txt`, and a python file started with `test` on the same directory level:

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

The `search_base_dirs` look like

```ini
search_base_dirs = backend1
                   backend2

```


`ignored_dir_names`: directories that the plugin should ignore in autodiscovery

Example:

```
ignored_dir_names = .serverless
                    .vscode

```

The directories with follow names is ignored by default

```
    .tox
    __pycache__
    eggs/
    .eggs/
    node_modules
```

if you want to override the default ignored directories names, use the option

```
default_ignored_dir_names
```

## Contributing


Contributions are very welcome. Tests can be run with
[tox](https://tox.readthedocs.io/en/latest/), please ensure the coverage
at least stays the same before you submit a pull request.

## License


Distributed under the terms of the
[MIT](http://opensource.org/licenses/MIT) license,
\"tox-lambda-autodiscovery\" is free and open source software

## Issues


If you encounter any problems, please [file an
issue](https://github.com/luzfcb/tox-lambda-autodiscovery/issues) along
with a detailed description.
