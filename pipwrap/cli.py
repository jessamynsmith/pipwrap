from __future__ import absolute_import

import argparse
import pkg_resources
import sys

from .command import Command


def create_parser():
    parser = argparse.ArgumentParser(
        description='Manage Python package requirements across multiple environments using '
                    'per-environment requirements files.')

    parser.add_argument('--version', action='store_true', default=False,
                        help="Show program's version number.")

    parser.add_argument('-r', '--requirements-files', action='store_true', default=False,
                        help='Generate or update requirements files.')

    parser.add_argument('-c', '--clean', action='store_true', default=False,
                        help='Remove packages from requirements files that are not installed in '
                             'virtualenv (only valid with -r).')

    parser.add_argument('-x', '--remove-extra', action='store_true', default=False,
                        help='Remove packages from virtualenv that are not present in requirements '
                             'files.')

    parser.add_argument('-l', '--lint', action='store_true', default=False,
                        help='Show discrepancies between requirements files and virtualenv.')

    return parser


def verify_args(args):
    has_one_option = (bool(args.requirements_files) ^ bool(args.remove_extra) ^ bool(args.lint))
    if not has_one_option:
        return 'Must specify --requirements-files (-r) or --remove-missing (-x) or --lint (-l).'
    if args.clean and not args.requirements_files:
        return '-c is only supported with -r'
    return None


def error(parser, message):
    parser.print_help()
    parser.exit(message="\nERROR: %s\n" % message)


def main():
    try:
        parser = create_parser()
        parsed_args = parser.parse_args()

        if parsed_args.version:
            parser.exit("pipwrap %s" % pkg_resources.require("pipwrap")[0].version)

        error_message = verify_args(parsed_args)
        if error_message:
            error(parser, error_message)
        command = Command(parsed_args)
        return command.run()
    except KeyboardInterrupt:
        sys.exit()
