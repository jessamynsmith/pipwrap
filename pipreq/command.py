try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os
import re
import subprocess
import sys

# In python 3, raw_input has been renamed to input
try:
    input = raw_input
except NameError:
    pass


class Command(object):

    LINE_REGEX = re.compile('(?P<package>[A-Za-z0-9.-]+)'
                            '(?:(?P<specifier>[=<>]{1,2})(?P<version>\S+))?\Z')

    def __init__(self, args, rc_filename):
        self.args = args
        self.rc_filename = rc_filename
        self.config = configparser.ConfigParser()
        # This open is required so that capitalization is kept when writing
        self.config.optionxform = str
        self.config.read(rc_filename)

    def _add_section(self, section):
        try:
            self.config.add_section(section)
        except configparser.DuplicateSectionError:
            pass

    def _set_option(self, section, option, value):
        self._add_section(section)
        self.config.set(section, option, value)

    def _get_option(self, option):
        for section in self.config.sections():
            try:
                return section, self.config.get(section, option)
            except configparser.NoOptionError:
                continue
        return None, None

    def _get_shared_section(self):
        try:
            return self.config.get('metadata', 'shared')
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
        return None

    def _make_requirements_directory(self, base_dir):
        requirements_dir = os.path.join(base_dir, 'requirements')
        if not os.path.exists(requirements_dir):
            os.makedirs(requirements_dir)
        return requirements_dir

    def _format_requirements_line(self, package, version):
        # TODO deal with <, > versions?
        version_spec = ''
        if version:
            version_spec = '==%s' % version
        return '%s%s\n' % (package, version_spec)

    def _write_requirements_file(self, shared, section, requirements, filename):
        req_file = open(filename, 'w+')
        if shared and section != shared:
            req_file.write('-r %s.txt\n' % shared)
        for package in sorted(requirements.keys()):
            req_file.write(self._format_requirements_line(package, requirements[package]))
        req_file.close()

    def generate_requirements_files(self, base_dir='.'):
        """ Generate set of requirements files for config """

        print("Creating requirements files\n")

        # TODO How to deal with requirements that are not simple, e.g. a github url

        shared = self._get_shared_section()

        requirements_dir = self._make_requirements_directory(base_dir)

        for section in self.config.sections():
            if section == 'metadata':
                continue

            requirements = {}
            for option in self.config.options(section):
                requirements[option] = self.config.get(section, option)

            if not requirements:
                # No need to write out an empty file
                continue

            filename = os.path.join(requirements_dir, '%s.txt' % section)
            self._write_requirements_file(shared, section, requirements, filename)

    def _remap_stdin(self):
        # Since stdin was taken by the input file, reconnect so we can get user input
        sys.stdin = open('/dev/tty')

    def _get_section_key(self):
        prompt = '> '
        return input(prompt)

    def _get_section(self, package, sections, section_text):
        print("Which section should package '%s' go into? %s" % (package, section_text))
        section = ''
        while not section:
            section_key = self._get_section_key()
            try:
                section = sections[int(section_key)]
            except (TypeError, ValueError, KeyError):
                print("'%s' is not a valid section. %s" % (section_key, section_text))
        return section

    def _write_default_sections(self):
        """ Starting from scratch, so create a default rc file """
        self.config.add_section('metadata')
        self.config.set('metadata', 'shared', 'common')
        self.config.add_section('common')
        self.config.add_section('development')
        self.config.add_section('production')

    def _parse_line(self, line):
        package = None
        version = ''
        match = self.LINE_REGEX.match(line.strip())
        if match:
            groups = match.groupdict()
            package = groups.get('package')
            version = groups.get('version', '')
        return package, version

    def create_rc_file(self, packages):
        """ Create a set of requirements files for config """

        print("Creating rcfile '%s'\n" % self.rc_filename)

        # TODO bug with == in config file

        if not self.config.sections():
            self._write_default_sections()

        sections = {}
        section_text = []
        for i, section in enumerate(self.config.sections()):
            if section == 'metadata':
                continue
            sections[i] = section
            section_text.append('%s. %s' % (i, section))
        section_text = ' / '.join(section_text)

        self._remap_stdin()
        package_names = set()
        lines = packages.readlines()
        for line in lines:
            package, version = self._parse_line(line)
            if not package:
                continue
            package_names.add(package)
            section, configured_version = self._get_option(package)
            # Package already exists in configuration
            if section:
                # If there is a configured version, update it. If not, leave it unversioned.
                if configured_version:
                    if configured_version != version:
                        print("Updating '%s' version from '%s' to '%s'"
                              % (package, configured_version, version))
                        self.config.set(section, package, version)
                continue

            section = self._get_section(package, sections, section_text)
            self._set_option(section, package, version)

        for section in self.config.sections():
            if section == 'metadata':
                continue
            for option in self.config.options(section):
                if option not in package_names:
                    print("Removing package '%s'" % option)
                    self.config.remove_option(section, option)

        rc_file = open(self.rc_filename, 'w+')
        self.config.write(rc_file)
        rc_file.close()

    def upgrade_packages(self, packages):
        """ Upgrade all specified packages to latest version """

        print("Upgrading packages\n")

        package_list = []
        lines = packages.readlines()
        for line in lines:
            package, version = self._parse_line(line)
            if package:
                package_list.append(package)

        if package_list:
            args = [
                "pip",
                "install",
                "-U",
            ]
            args.extend(package_list)
            subprocess.check_call(args)
        else:
            print("No packages to upgrade")

    def remove_extra_packages(self, packages):
        """ Remove all packages missing from list """

        print("Removing packages\n")

        args = [
            "pip",
            "freeze",
        ]
        installed = subprocess.check_output(args, universal_newlines=True)

        installed_list = set()
        for line in installed.strip().split('\n'):
            package, version = self._parse_line(line)
            installed_list.add(package)

        package_list = set()
        for line in packages.readlines():
            package, version = self._parse_line(line)
            package_list.add(package)

        removal_list = installed_list - package_list
        if removal_list:
            args = [
                "pip",
                "uninstall",
                "-y",
            ]
            args.extend(list(removal_list))
            subprocess.check_call(args)
        else:
            print("No packages to be removed")

    def run(self, base_dir='.'):
        if self.args.generate:
            self.generate_requirements_files(base_dir)
        elif self.args.create:
            self.create_rc_file(self.args.packages)
        elif self.args.upgrade:
            self.upgrade_packages(self.args.packages)
        elif self.args.remove_extra:
            self.remove_extra_packages(self.args.packages)
