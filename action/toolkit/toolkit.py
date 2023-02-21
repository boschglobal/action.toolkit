# SPDX-FileCopyrightText: 2023 Robert Bosch GmbH
#
# SPDX-License-Identifier: Apache-2.0

"""Toolkit module providing methods for the efficient implementation of GitHub
Actions.


Example
-------
This example shows how to use these toolkit methods::

    from action.toolkit import ActionSpec, action_main

    def my_set_defaults_func(args):
        return args

    def my_do_action_func(args):
        return { 'foo': 'bar' }

    spec = ActionSpec(
        filename = 'action.yaml',
        name = 'foo',
        long_name = 'foo bar',
        description = 'fubar',
        set_defaults = my_set_defaults_func,
        do_action = my_do_action_func,
    )
    action_main(spec)
"""

from __future__ import annotations
from typing import Sequence, Optional, Dict, Callable, Tuple, Any
from dataclasses import dataclass
from collections import namedtuple
import argparse
import logging
import os
import os.path
import yaml


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ActionSpec:
    """Action Specification. Various fields and functions which control the
    behaviour of the Action.

    Parameters
    ----------
    filename: str
        Relative path to the `action.yaml` file which defines the parameters
        of the Action.
    name: str
        The (short) name of the Action.
    long_name: str
        The longer name of the Action.
    description: str
        A description of the Action.
    env_prefix: str
        Prefix used when resolving environment variables.
    set_defaults: Callable
        This function will set any default values for the Action.
    do_action: Callable
        This function will perform the Action.
    """
    filename: str
    name: str
    long_name: str = None
    description: str = None
    env_prefix: str = None
    set_defaults: Callable[[Dict[str, str]], Dict[str, str]] = None
    do_action: Callable[[Dict[str, str]], Dict[str, str]] = None

    def __post_init__(self):
        self.long_name = self.long_name or self.name
        self.description = self.description or self.name
        self.env_prefix = self.env_prefix or self.name


def get_env(envar_list: Sequence[str], default: Optional[str] = None) -> str:
    """Resolve an Environment Variables, according to priority.

    Each element in the ``envar_list`` list is attempted until an Environment
    Variable is successfully resolved, which is then returned to the caller. If
    none of the elements successfully resolves then the specified default
    value is returned to the caller.

    Note
    ----
    Empty strings are converted to None.

    Parameters
    ----------
    envar_list : list of str
        List of Environment Variables to resolve.
    default: str
        The default value to return if no Environment Variable can be resolved.

    Returns
    -------
    str
        The resolved Environment Variable.
    """
    for _ in envar_list:
        value = os.getenv(_, None)
        if value:  # Only return on non-empty strings.
            return value
    return default


def parse_arguments(action_spec: ActionSpec) -> Tuple[Dict[str, str], bool]:
    """Parse arguments and resolve parameters.

    Arguments are taken from the CLI first, then the Environment, and lastly
    the default value (if specified). Default values, specified in the
    ``action.yaml`` file, have any included environment variables expanded.

    The ``action.yaml`` is formatted as follows::

        ---
        name: 'SomeAction'
        description: 'SomeAction GitHub Action.'
        inputs:
          user:
            description: 'User name.'
            required: false
          token:
            description: 'API Key for the User.'
            required: false
            default: '${GHE_TOKEN}'

    Parameters
    ----------
    action_spec.filename : str
        Path to ``action.yaml`` file where Action inputs are defined.

    Returns
    -------
    dict of {str : str}
        Dictionary of arguments, from the call to ``parser.parse_args()``.
    bool
        Indicates if any required arguments were missing.
    """
    # Parse the arguments from the "action.yaml" file.
    ArgSpec = namedtuple('ArgSpec',
            ['name', 'default', 'help', 'required'], 
            defaults=[False])
    arguments = list()
    with open(action_spec.filename) as f:
        y = yaml.load(f.read(), Loader=yaml.SafeLoader)
        for input in y['inputs']:
            input_dict = y['inputs'][input]
            default = input_dict.get('default', None)
            if isinstance(default, str):
                default = os.path.expandvars(default)
            arguments.append(ArgSpec(
                input,
                default,
                input_dict.get('help', None),
                input_dict.get('required', False),
            ))
    parser = argparse.ArgumentParser(description=action_spec.description)
    for arg_spec in arguments:
        parser.add_argument(
            f"--{arg_spec.name}",
            required=False,
            type=str,
            default=get_env([
                (
                    f"{action_spec.env_prefix.replace(' ','').upper()}"
                    f"_{arg_spec.name.upper()}"
                ),
                f"INPUT_{arg_spec.name.upper()}",
            ], arg_spec.default),
            help=arg_spec.help,
        )
    args = parser.parse_args()
    # Check that all required arguments are present.
    missing_args = False
    for arg_spec in arguments:
        if arg_spec.required:
            if arg_spec.name not in args:
                missing_args = True
                logger.error('Missing required argument %s', arg_spec.name)
    # Return args, and missing args condition.
    return args, missing_args


def action_main(action_spec: ActionSpec) -> Dict[str, Any]:
    """Action main function which should be called by the Action.

    Parameters
    ----------
    action_spec : ActionSpec
        ActionSpec object defining the Action parameters and behaviour.

    Returns
    -------
    dict of {str : Any}
        Dictionary of outputs, from the call to ``action_spec.do_action()``.
    """
    args, missing_args = parse_arguments(action_spec)
    args = vars(args) # Trims the Namespace object.
    if action_spec.set_defaults:
        args = action_spec.set_defaults(args)

    logger.info('%s, with arguments:', action_spec.long_name)
    for arg, val in sorted(args.items()):
        if arg == 'token':
            logger.info('  %s=********:', arg)
            continue
        logger.info('  %s=%s:', arg, val)

    if missing_args:
        logger.error('Some required arguments are missing!')
        exit(1)

    # Call the Action implementation.
    if action_spec.do_action:
        outputs = action_spec.do_action(args)
        # Print the outputs (which get picked up by GitHub Action Runners).
        for name, result in outputs.items():
            print(f'::set-output name={name}::{result}')
        # Unit Test Support
        #  GitHub will intercept STDOUT and "capture" any lines starting with
        #  '::'. Therefore, to support unit testing, print the results a second
        #  time without the '::'' prefix.
        for name, result in outputs.items():
            print(f'set-output name={name}::{result}')
        return outputs
    return {}
