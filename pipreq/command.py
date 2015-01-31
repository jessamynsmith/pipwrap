import ConfigParser
import os
import sys


class Command(object):

    def __init__(self, args):
        self.args = args

    def print_message(self, message, verbosity_needed=1):
        """ Prints the message, if verbosity is high enough. """
        if self.args.verbosity >= verbosity_needed:
            print message

    def error(self, message, code=1):
        """ Prints the error, and exits with the given code. """
        print >>sys.stderr, message
        sys.exit(code)

    def _get_config_parser(self):
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        return config

    def _parse_rc_file(self, rc_file):
        config = self._get_config_parser()
        config.read(rc_file)
        return config

    def _add_section(self, config, section):
        try:
            config.add_section(section)
        except ConfigParser.DuplicateSectionError:
            pass

    def _set_option(self, config, section, option, value):
        self._add_section(config, section)
        config.set(section, option, value)

    def _get_option(self, config, option):
        for section in config.sections():
            try:
                return section, config.get(section, option)
            except ConfigParser.NoOptionError:
                continue
        return None, None

    def _format_requirements_line(self, package, version):
        # TODO deal with <, > versions?
        return '%s==%s\n' % (package, version)

    def generate_requirements_files(self):
        print "Creating requirements files\n"

        config = self._parse_rc_file(".requirementsrc")

        # TODO read in existing files? what about special requirements like urls

        try:
            shared = config.get('metadata', 'shared')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            shared = None

        if not os.path.exists('requirements'):
            os.makedirs('requirements')

        for section in config.sections():
            if section == 'metadata':
                continue

            requirements = {}
            for option in config.options(section):
                requirements[option] = config.get(section, option)

            if not requirements:
                # No need to write out an empty file
                continue

            req_file = open('requirements/%s.txt' % section, 'w+')
            if shared and section != shared:
                req_file.write('-r %s.txt\n' % shared)
            for package in sorted(requirements.keys()):
                req_file.write(self._format_requirements_line(package, requirements[package]))
            req_file.close()

    def create_rc_file(self, packages):
        print "Creating rcfile '%s'\n" % ".requirementsrc"

        prompt = '> '

        config = self._parse_rc_file(".requirementsrc")

        if not config.sections():
            # Starting from scratch, so create a default rc file
            config.add_section('metadata')
            config.set('metadata', 'shared', 'common')
            config.add_section('common')
            config.add_section('development')
            config.add_section('production')

        i = 1
        sections = {}
        section_text = []
        for section in config.sections():
            if section == 'metadata':
                continue
            sections[i] = section
            section_text.append('%s. %s' % (i, section))
            i += 1
        section_text = ' / '.join(section_text)

        package_names = set()
        for line in packages.readlines():
            package, version = line.strip().split('==')
            package_names.add(package)
            section, configured_version = self._get_option(config, package)
            if configured_version:
                if configured_version != version:
                    print ("Updating '%s' version from '%s' to '%s'"
                           % (package, configured_version, version))
                    config.set(section, package, version)
                continue

            print "Which section should package '%s' go into? %s" % (package, section_text)
            section = ''
            while not section:
                section_key = raw_input(prompt)
                try:
                    section = sections[int(section_key)]
                except (ValueError, KeyError):
                    print "'%s' is not a valid section. %s" % (section_key, section_text)
            self._set_option(config, section, package, version)

        for section in config.sections():
            if section == 'metadata':
                continue
            for option in config.options(section):
                if option not in package_names:
                    print "Removing package '%s'" % option
                    config.remove_option(section, option)

        rc_file = open('.requirementsrc', 'w+')
        config.write(rc_file)
        rc_file.close()

    def run(self):
        if self.args.generate:
            self.generate_requirements_files()
        elif self.args.create:
            self.create_rc_file(self.args.packages)
