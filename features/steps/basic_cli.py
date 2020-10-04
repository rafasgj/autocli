# This file is part of autocli
#
# Copyright (C) 2020 Rafael Guterres Jeffman
#
# f/π is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Foobar is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <https://www.gnu.org/licenses/>.

"""Basic CLI test steps."""

import sys
import io
from unittest.mock import MagicMock
import yaml

# pylint: disable=import-error, no-name-in-module
from behave import given, when, then

from autocli import AutoCLI


def __run_application(context, params=None):
    try:
        context.cli.run(params)
    except SystemExit as sysexit:
        context.exit_code = sysexit.code
        context.exception = None
    except Exception as exception:  # pylint: disable=broad-except
        context.exception = exception
        context.exit_code = float("NaN")
    else:
        context.exception = None
        context.exit_code = 0


def __compare_output(expected, observed):
    expected = expected.strip()
    observed = observed.strip()
    msg = "Output mismatch: size = %d / %d\n---\n%s\n===\n%s\n---\n" % (
        len(expected),
        len(observed),
        expected,
        observed,
    )
    assert observed == expected, msg


@given("the CLI description")
def _given_cli_description(context):
    """Create AutoCLI from YAML/JSON text data."""
    context.cli_description = yaml.safe_load(context.text)
    context.cli = AutoCLI(context.cli_description)


@given('a function "{func}" with an argument "{arg}" that prints "{strfmt}"')
def _given_a_function_with_one_arg_that_prints(context, func, arg, strfmt):
    # pylint: disable=unused-argument
    def side_effect(**kwargs):
        print(strfmt.format(**kwargs))

    *module, function = func.split(".")
    context.mock_fun = MagicMock(
        **{function: MagicMock(side_effect=side_effect)}
    )
    sys.modules[".".join(module)] = context.mock_fun


@when("the application is executed without prameters")
def _when_run_application_without_parameters(context):
    __run_application(context, None)


@then("the output is")
def _then_output_is(context):
    __compare_output(context.text, context.stdout.getvalue())
    context.stdout = io.StringIO()


@then("the error output is")
def _then_error_output_is(context):
    __compare_output(context.text, context.stderr.getvalue())
    context.stderr = io.StringIO()


@then("the exit code is not zero")
def _then_exit_code_is_not_zero(context):
    assert context.exit_code != 0


@then("the exit code is zero")
def _then_exit_code_is_zero(context):
    assert context.exit_code == 0


@then("the exit code is {exit_code:d}")
def _then_exit_code_is(context, exit_code):
    assert context.exit_code == exit_code, "exit_code: %d / %d" % (
        context.exit_code,
        exit_code,
    )


@when("the application is executed with [{param_list}]")
def _when_run_application_with_param(context, param_list):
    params = [p.strip() for p in param_list.split(",")]
    __run_application(context, params)


@then('the CLI configuration has attribute "{attribute}" with value {value}')
def _then_cli_configuration_has_attribute(context, attribute, value):
    assert hasattr(context.cli.configuration, attribute)
    assert str(getattr(context.cli.configuration, attribute)) == value