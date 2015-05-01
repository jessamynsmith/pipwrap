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

    parser.add_argument('-x', '--remove-extra', action='store_true', default=False,
                        help='Remove packages not in list (requires list of packages).')

    parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                        help='Don\'t actually make any changes; '
                             'only show what would have been done.')

    return parser


def verify_args(args):
    has_one_option = (bool(args.requirements_files) ^ bool(args.remove_extra))
    if not has_one_option:
        return 'Must specify requirements-files (-r) or remove-missing (-x).'
    if args.dry_run and not args.remove_extra:
        return '-n is only supported with -x'
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
        command.run()
        return 0
    except KeyboardInterrupt:
        sys.exit()
