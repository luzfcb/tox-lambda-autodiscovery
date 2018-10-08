# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path

import pluggy
import tox.config
from tox.config import _ArgvlistReader
from py._path.local import LocalPath

hookimpl = pluggy.HookimplMarker("tox")

log = logging.getLogger('lambda-autodiscovery')

ENV_CONFIG_NAME = 'lambdaautodiscovery'
ENV_PREFIX = 'lambda'
SECTION_PREFIX = 'testenv'
SECTION_NAME = '{}:{}'.format(SECTION_PREFIX, ENV_CONFIG_NAME)

RE_REQUIREMENTS_FILE = re.compile(r'^(requirements\.txt)$')
RE_TEST_FILES = re.compile(r'^(test(.*)\.py)$')

default_ignored = [
    '.tox',
    '__pycache__',
    'eggs/',
    '.eggs/',
    'node_modules'
]


@hookimpl
def tox_configure(config):
    if not config._cfg.sections.get(SECTION_NAME):
        return
    reader = tox.config.SectionReader(SECTION_NAME, config._cfg)
    # workaround: used to generate the 'commands' on new tox testenv
    commands_template = reader.getstring('commands_workaround', replace=False)

    try:
        # remove 'lambdaautodiscovery' section from available tox testenv
        config.envlist.remove(ENV_CONFIG_NAME)
    except ValueError:  # this error is raised if 'tox -e'
        pass

    # add current_toxenv_lambda_dir and current_toxenv_name
    # to make tox happy, and not get an error
    reader.addsubstitutions(current_toxenv_lambda_dir='')
    reader.addsubstitutions(current_toxenv_name='')

    coveragerc_file = Path(config.toxinidir, '.coveragerc')
    has_coveragerc_file = False
    if coveragerc_file.exists():
        has_coveragerc_file = True

    # extracted fom tox-travis
    distshare_default = "{homedir}/.tox/distshare"
    reader.addsubstitutions(toxinidir=config.toxinidir,
                            homedir=config.homedir)

    reader.addsubstitutions(toxworkdir=config.toxworkdir)
    config.distdir = reader.getpath("distdir", "{toxworkdir}/dist")
    reader.addsubstitutions(distdir=config.distdir)
    config.distshare = reader.getpath("distshare", distshare_default)
    reader.addsubstitutions(distshare=config.distshare)
    # end

    search_base_dirs = reader.getlist('search_base_dirs')

    default_ignored_dir_names_from_config = reader.getlist('default_ignored_dir_names')
    ignored_dir_names = reader.getlist('ignored_dir_names')

    if default_ignored_dir_names_from_config:
        ignored_dir_names.extend(default_ignored_dir_names_from_config)
    else:
        ignored_dir_names.extend(default_ignored)

    ignored_dir_names = set(ignored_dir_names)

    ignored_dir_names_regex = build_compiled_regex(ignored_dir_names)

    # help to customize PYTHONPATH
    setenv_dict = reader.getdict_setenv('setenv')
    if setenv_dict:
        pythonpath_template = setenv_dict.get('PYTHONPATH')
    else:
        pythonpath_template = None

    if not search_base_dirs:
        search_base_dirs = [config.toxinidir]

    deps = reader.getlist('deps')

    search_base_dirs = set(search_base_dirs)
    new_envs_configs = []
    for directory in search_base_dirs:
        sub_directory = Path(config.toxinidir, directory)
        if sub_directory.exists():
            # TODO: handle duplicate envname
            new_envs_configs.extend(
                find_dirs_with_test_files_and_requirements_file(sub_directory, ignored_dir_names_regex))

    # extracted fom tox-travis
    try:
        make_envconfig = tox.config.ParseIni.make_envconfig  # tox 3.4.0+
    except AttributeError:
        make_envconfig = tox.config.parseini.make_envconfig
    # Dig past the unbound method in Python 2
    make_envconfig = getattr(make_envconfig, '__func__', make_envconfig)
    # end

    for env in reversed(new_envs_configs):
        env_name = env.get('envname')
        _dir = env.get('dir')
        dir_str = str(_dir)
        section_name = '{}{}'.format(tox.config.testenvprefix, env_name)

        # create new tox testenv
        new_env = make_envconfig(
            config, env_name, section_name, reader._subs, config)

        new_env.changedir = _dir
        substitutions = reader._subs.copy()
        substitutions.update({
            'changedir': _dir,
            'current_toxenv_lambda_dir': _dir,
            'current_toxenv_name': env_name,
            'envtmpdir': str(new_env.envtmpdir)
        })
        reader.addsubstitutions(**substitutions)

        # generate the command from 'temp_commands'
        commands = _ArgvlistReader.getargvlist(reader, commands_template, replace=True)
        new_env.commands.extend(commands)

        current_tox_env_pythonpath = [dir_str]
        if pythonpath_template:
            current_tox_env_pythonpath.extend(pythonpath_template.split(':'))

        new_env.setenv['PYTHONPATH'] = ':'.join(current_tox_env_pythonpath)

        # configure coverage files
        # https://pytest-cov.readthedocs.io/en/latest/plugins.html
        new_env.setenv['COV_CORE_SOURCE'] = dir_str
        # new_env.setenv['COV_CORE_DATAFILE'] = str(Path(config.toxinidir, '.coverage.{}'.format(env_name)))

        # try append coverage file, in a single file.
        new_env.setenv['COV_CORE_DATAFILE'] = str(Path(config.toxinidir, '.coverage'))
        if has_coveragerc_file:
            new_env.setenv['COV_CORE_CONFIG'] = str(coveragerc_file)

        # # inject in the 'new_env' tox testenv, the dependencies defined in lambdaautodiscovery
        for dep in deps:
            new_env.deps.append(tox.config.DepConfig(name=dep))

        # inject the absolute path to requirements.txt file of current lambda
        lambda_requirements_file = _dir.join('requirements.txt')
        dep_config = tox.config.DepConfig(name='-r{}'.format(lambda_requirements_file))
        new_env.deps.append(dep_config)

        config.envconfigs[env_name] = new_env
        # TODO: find a safe way to verify when tox is running via tox -e
        # and only add 'env_name' if -e options is equal to 'env_name'
        config.envlist.insert(0, env_name)

    config.envlist.insert(0, ENV_CONFIG_NAME)


def build_compiled_regex(ignored_dirs_regex):
    regex = r'|'.join(ignored_dirs_regex)
    regex = regex.replace('.', r'\.')
    regex = regex.replace('*', r'(.*)')
    regex = r'.*({}).*'.format(regex)
    return re.compile(regex)


def find_dirs_with_test_files_and_requirements_file(path, ignored_dir_names_regex):
    """
    Recursively, lists all directories from `path`,
    excludes ignored directories from the list
    For each directory, check that it contains, at the same level,
    a `requirements.txt` file and files startwith `test` and endwith `.py`

    :param path: pathlib.Path object
    :param ignored_dir_names_regex:
    :return: list of dicts on format
        [{'dir': py._path.local.LocalPath object, 'envname': str }, ]
    """
    dirs = []

    for directory in path.glob('**/'):
        directory_str = str(directory)
        if not ignored_dir_names_regex.match(directory_str):
            dir_contains_requirements_file = False
            dir_contains_test_files = False

            # list only the files of directory
            filenames = (file.name for file in directory.iterdir() if file.is_file())

            for filename in filenames:

                if RE_REQUIREMENTS_FILE.match(filename):
                    dir_contains_requirements_file = True

                if RE_TEST_FILES.match(filename):
                    dir_contains_test_files = True

            if dir_contains_requirements_file and dir_contains_test_files:
                # tox require a py._path.local.LocalPath instance.
                directory_local_path = LocalPath(str(directory))
                dirs.append(
                    dict(
                        dir=directory_local_path,
                        envname='{}-{}'.format(ENV_PREFIX, directory.parts[-1])
                    )
                )

    return dirs
