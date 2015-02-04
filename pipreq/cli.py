import argparse
import sys

from pipreq.command import Command


def create_parser():
    parser = argparse.ArgumentParser(
        description='Manage Python package requirements across multiple environments using '
                    'per-environment requirements files.')

    parser.add_argument('-g', '--generate', action='store_true', default=False,
                        help='Generate requirements files')
    parser.add_argument('-c', '--create', action='store_true', default=False,
                        help='Create or update rc file (requires list of packages)')
    parser.add_argument('-U', '--upgrade', action='store_true', default=False,
                        help='Upgrade packages (requires list of packages)')
    parser.add_argument('packages', nargs='?', type=argparse.FileType('r'), default=sys.stdin)

    return parser


def verify_args(args):
    if not args.create and not args.generate and not args.upgrade:
        return 'Must specify generate (-g) or create/upgrade (-[cu]) with packages'
    return None


def error(parser, message):
        parser.print_help()
        parser.exit(message="\nERROR: %s\n" % message)


def main():
    try:
        parser = create_parser()
        parsed_args = parser.parse_args()
        error_message = verify_args(parsed_args)
        if error_message:
            error(parser, error_message)
        command = Command(parsed_args, ".requirementsrc")
        command.run()
    except KeyboardInterrupt:
        sys.exit()
