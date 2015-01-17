import argparse
import ConfigParser
import os


def _get_config_parser():
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    return config


def _parse_rc_file(rc_file):
    config = _get_config_parser()
    config.read(rc_file)
    return config


def generate_requirements_files():
    config = _parse_rc_file(".requirementsrc")

    shared = None
    for section in config.sections():
        if config.has_option(section, 'shared') and config.get(section, 'shared'):
            if shared:
                print "Can only have one section with 'shared=True'"
                return -1
            shared = section
            config.remove_option(section, 'shared')

    if not os.path.exists('requirements'):
        os.makedirs('requirements')

    for section in config.sections():
        req_file = open('requirements/%s.txt' % section, 'w+')
        if shared and section != shared:
            req_file.write('-r %s.txt\n' % shared)
        for option in config.options(section):
            req_file.write('%s==%s\n' % (option, config.get(section, option)))
        req_file.close()


def create_rc_file(packages):
    prompt = '> '
    sections = {'c': 'common', 'd': 'development', 'p': 'production'}
    section_text = 'c(ommon)/d(evelopment)/p(roduction)'

    config = _get_config_parser()
    for line in packages.readlines():
        package, version = line.strip().split('==')
        print "Which section should package '%s' go into? %s" % (package, section_text)
        section = ''
        while not section:
            section_key = raw_input(prompt)
            try:
                section = sections[section_key]
            except KeyError:
                print "'%s' is not a valid section. %s" % (section_key, section_text)
        try:
            config.add_section(section)
        except ConfigParser.DuplicateSectionError:
            pass
        config.set(section, package, version)

    rc_file = open('.requirementsrc', 'w+')
    config.write(rc_file)
    rc_file.close()


def main():
    cli_parser = argparse.ArgumentParser()
    cli_parser.add_argument('-g', '--generate', action='store_true',
        default=False, help='generate requirements files')
    cli_parser.add_argument('-c', '--create', action='store_true',
        default=False, help='create rc file')
    cli_parser.add_argument('-p', '--packages', type=argparse.FileType('r'),
        default=False, help='list of installed packages (e.g. pip freeze)')
    cli_args = cli_parser.parse_args()

    if cli_args.generate:
        generate_requirements_files()
    elif cli_args.create:
        if not cli_args.packages:
            cli_parser.error("Create (-c) requires a list of packages (-p)")
        create_rc_file(cli_args.packages)
    else:
        print "Must specify -g or -c and -p\n"
        print cli_parser.print_help()


if __name__ == '__main__':
    main()
