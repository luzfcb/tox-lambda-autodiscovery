# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path

import pluggy
import tox.config

hookimpl = pluggy.HookimplMarker("tox")

log = logging.getLogger('lambda-autodiscovery')

SECTION_NAME = 'testenv:lambdaautodiscovery'

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

    if not search_base_dirs:
        search_base_dirs = [config.toxinidir]

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

    for env in new_envs_configs:
        env_name = env.get('envname')
        _dir = env.get('dir')
        dir_str = str(_dir)
        section = tox.config.testenvprefix + env_name
        new_env = make_envconfig(
            config, env_name, section, reader._subs, config)
        new_env.changedir = _dir
        new_env.setenv['PYTHONPATH'] = str(_dir)

        # https://pytest-cov.readthedocs.io/en/latest/plugins.html
        new_env.setenv['COV_CORE_SOURCE'] = dir_str
        new_env.setenv['COV_CORE_DATAFILE'] = str(Path(config.toxinidir, '.coverage.{}'.format(env_name)))
        coveragerc_file = Path(config.toxinidir, '.coveragerc')
        if coveragerc_file.exists():
            new_env.setenv['COV_CORE_CONFIG'] = str(coveragerc_file)

        dep_path = _dir.joinpath('requirements.txt')
        dep_config = tox.config.DepConfig(name='-r{}'.format(dep_path))
        new_env.deps.append(dep_config)

        config.envconfigs[env_name] = new_env
        config.envlist.append(env_name)


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
        [{'dir': pathlib.Path object, 'envname': str }, ]
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
                dirs.append(
                    dict(
                        dir=directory,
                        envname='lambda-{}'.format(directory.parts[-1])
                    )
                )

    return dirs
