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

    def _get_option(self, config, option):
        for section in config.sections():
            try:
                return section, config.get(section, option)
            except ConfigParser.NoOptionError:
                continue
        return None, None

    def _format_requirements_line(self, package, version):
        return '%s==%s\n' % (package, version)

    def generate_requirements_files(self):
        config = self._parse_rc_file(".requirementsrc")
        # TODO make [metadata] section with shared=<common>

        shared = None
        for section in config.sections():
            if config.has_option(section, 'shared') and config.get(section, 'shared'):
                if shared:
                    self.error("Can only have one section with 'shared=True'")
                shared = section
                config.remove_option(section, 'shared')

        if not os.path.exists('requirements'):
            os.makedirs('requirements')

        for section in config.sections():
            req_file = open('requirements/%s.txt' % section, 'w+')
            if shared and section != shared:
                req_file.write('-r %s.txt\n' % shared)
            for option in config.options(section):
                req_file.write(self._format_requirements_line(option, config.get(section, option)))
            req_file.close()

    def create_rc_file(self, packages):
        prompt = '> '
        sections = {'c': 'common', 'd': 'development', 'p': 'production'}
        section_text = 'c(ommon)/d(evelopment)/p(roduction)'

        config = self._parse_rc_file(".requirementsrc")

        for line in packages.readlines():
            package, version = line.strip().split('==')
            section, configured_version = self._get_option(config, package)
            if configured_version:
                if configured_version != version:
                    print ("Updating %s version from %s to %s"
                           % (package, configured_version, version))
                    config.set(section, package, version)
                continue

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

    def run(self):
        if self.args.generate:
            self.generate_requirements_files()
        elif self.args.create:
            self.create_rc_file(self.args.packages)
