import argparse

from pipreq.command import Command


def create_parser():
    parser = argparse.ArgumentParser(
        description='Manage Python package requirements across multiple environments using '
                    'per-environment requirements files.')

    parser.add_argument('-g', '--generate', action='store_true', default=False,
                        help='Generate requirements files')
    parser.add_argument('-c', '--create', action='store_true', default=False,
                        help='Create (or update) rc file')
    parser.add_argument('-p', '--packages', type=argparse.FileType('r'), default=False,
                        help='list of installed packages (e.g. pip freeze)')

    return parser


def verify_args(args):
    if args.create and not args.packages:
            return 'Create (-c) requires a list of packages (-p)'
    elif not args.generate:
        return 'Must specify generate (-g) or create (-c) with packages (-p)'
    return None


def error(parser, message):
        parser.print_help()
        parser.exit(message="\nERROR: %s\n" % message)


def main():
    parser = create_parser()
    parsed_args = parser.parse_args()
    error_message = verify_args(parsed_args)
    if error_message:
        error(parser, error_message)
    command = Command(parsed_args)
    command.run()
