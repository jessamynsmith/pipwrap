import argparse
import pkg_resources
import sys

from pipreq.command import Command


def create_parser():
    parser = argparse.ArgumentParser(
        description='Manage Python package requirements across multiple environments using '
                    'per-environment requirements files.')

    parser.add_argument('--version', action='store_true', default=False,
                        help="Show program's version number")
    parser.add_argument('-g', '--generate', action='store_true', default=False,
                        help='Generate requirements files')
    parser.add_argument('-c', '--create', action='store_true', default=False,
                        help='Create or update rc file (requires list of packages)')
    parser.add_argument('-U', '--upgrade', action='store_true', default=False,
                        help='Upgrade packages (requires list of packages)')
    parser.add_argument('-x', '--remove-extra', action='store_true', default=False,
                        help='Remove packages not in list (requires list of packages)')
    parser.add_argument('packages', nargs='?', type=argparse.FileType('r'), default=sys.stdin)

    return parser


def verify_args(args):
    has_one_option = (bool(args.create) ^ bool(args.generate) ^ bool(args.upgrade)
                      ^ bool(args.remove_extra))
    if not has_one_option:
        return 'Must specify generate (-g) or create/upgrade/remove-missing (-[cur]) with packages'
    return None


def error(parser, message):
        parser.print_help()
        parser.exit(message="\nERROR: %s\n" % message)


def main():
    try:
        parser = create_parser()
        parsed_args = parser.parse_args()

        if parsed_args.version:
            parser.exit("pipreq %s" % pkg_resources.require("pipreq")[0].version)

        error_message = verify_args(parsed_args)
        if error_message:
            error(parser, error_message)
        command = Command(parsed_args, ".requirementsrc")
        command.run()
        return 0
    except KeyboardInterrupt:
        sys.exit()
