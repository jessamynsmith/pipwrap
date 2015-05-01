import os
import subprocess

# In python 3, raw_input has been renamed to input
try:
    input = raw_input
except NameError:
    pass

import requirements


def get_key(requirement):
    key = requirement.name
    if not key:
        key = requirement.path
    return key


class RequirementsFile(object):

    def __init__(self):
        self.included_files = []
        self.packages = set()


class Command(object):

    def __init__(self, args, base_dir='.'):
        self.args = args
        self.requirements_dir = os.path.join(base_dir, 'requirements')
        if not os.path.exists(self.requirements_dir):
            os.makedirs(self.requirements_dir)

    def _get_filename_key(self, prompt):
        return input(prompt)  # pragma nocover

    def _get_filename(self, package, filenames, filename_text):
        print("Which file should package '%s' go into? %s" % (package, filename_text))
        prompt = '> '
        filename = ''
        while not filename:
            filename_key = self._get_filename_key(prompt)
            try:
                filename = filenames[int(filename_key)]
            except (TypeError, ValueError, KeyError):
                print("'%s' is not a valid filename. %s" % (filename_key, filename_text))
        return filename

    def _format_requirements_line(self, package):
        if package.uri or package.path:
            text = package.line
        else:
            specs = ['%s%s' % (spec[0], spec[1]) for spec in package.specs]
            text = '%s%s' % (package.name, ','.join(specs))
        return '%s\n' % text

    def _write_requirements_file(self, req_file, filename):
        filename = os.path.join(self.requirements_dir, filename)
        with open(filename, 'w+') as req_output_file:
            req_output_file.writelines(req_file.included_files)
            for package in sorted(req_file.packages, key=get_key):
                req_output_file.write(self._format_requirements_line(package))

    def _get_installed_packages(self):
        """ Get a set of installed packages
        :return: Set of installed packages
        """
        args = [
            "pip",
            "freeze",
        ]
        installed = subprocess.check_output(args, universal_newlines=True)
        return set(requirements.parse(installed))

    def _get_requirements_from_files(self):
        """ Get a dictionary, keyed by filename, of requirements per file
        :return: Dictionary, keyed by filename, of requirements per file
        """
        req_files = {}
        for req_filename in os.listdir(self.requirements_dir):
            with open(os.path.join(self.requirements_dir, req_filename)) as requirements_file:
                req_file = RequirementsFile()
                for line in requirements_file.readlines():
                    if line.strip().startswith('-r'):
                        req_file.included_files.append(line)
                    requirements_file.seek(0)
                req_file.packages = set(requirements.parse(requirements_file))
            req_files[req_filename] = req_file
        return req_files

    def _compare_installed_and_required(self, installed_set, requirement_files):
        """ Updates required versions to installed versions, and finds all installed packages
            that are not in requirements
        :param installed_set: Set of installed packages
        :param requirement_files: Dictionary of required packages, keyed by filename
        :return: Tuple of (updated_installed_set, installed_not_in_requirements)
        """
        missing_set = installed_set.copy()
        for req_file in requirement_files:
            for requirement in requirement_files[req_file].packages:
                for installed in installed_set:
                    if installed.name == requirement.name:
                        requirement.specs = installed.specs
                        missing_set.remove(installed)
                        break
        return requirement_files, missing_set

    def generate_requirements_files(self):
        """ Create or update requirements files """
        print("Creating/updating requirements files\n")

        installed_reqs = self._get_installed_packages()
        req_files = self._get_requirements_from_files()
        (req_files, missing_reqs) = self._compare_installed_and_required(installed_reqs, req_files)

        filenames = {}
        filename_text = []
        filename_list = sorted(req_files.keys())
        if len(filename_list) < 1:
            default_filename = 'requirements.txt'
            req_files[default_filename] = RequirementsFile()
            filename_list.append(default_filename)
        for i, filename in enumerate(filename_list):
            filenames[i] = filename
            filename_text.append('%s. %s' % (i, filename))
        filename_text = ' / '.join(filename_text)

        # Add missing requirements to user-selected file
        for requirement in missing_reqs:
            filename = self._get_filename(requirement.name, filenames, filename_text)
            req_files[filename].packages.add(requirement)

        for req_filename in req_files:
            self._write_requirements_file(req_files[req_filename], req_filename)

        return 0

    def _determine_extra_packages(self):
        """ Determine all packages that are installed, but missing from requirements files
        :return: Set of packages to be removed
        """

        installed_set = self._get_installed_packages()
        req_files = self._get_requirements_from_files()
        req_files, removal_set = self._compare_installed_and_required(installed_set, req_files)
        return removal_set

    def remove_extra_packages(self):
        """ Remove all packages missing from list """

        removal_set = self._determine_extra_packages()
        if not removal_set:
            print("No packages to be removed")
        else:
            package_names = [package.name for package in removal_set]
            if self.args.dry_run:
                print("The following packages would be removed:\n    %s\n" %
                      "\n    ".join(package_names))
            else:
                print("Removing packages\n")
                args = [
                    "pip",
                    "uninstall",
                    "-y",
                ]
                args.extend(package_names)
                subprocess.check_call(args)

        return 0

    def run(self):
        result = 1
        if self.args.requirements_files:
            result = self.generate_requirements_files()
        elif self.args.remove_extra:
            result = self.remove_extra_packages()
        return result
