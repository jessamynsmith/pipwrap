import os
import sys
from mock import MagicMock, patch
import shutil
import tempfile
import unittest

from pipwrap import cli, command


def get_key(requirement):
    return requirement.line


def _create_requirements_file(output_dir, filename='packages.txt',
                              content='-r common.txt\nmock==1.2\nDjango==1.7\nnose==1.3\n'):
    filename = os.path.join(output_dir, filename)
    with open(filename, 'w') as packages:
        packages.write(content)


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.parser = cli.create_parser()
        tempdir = tempfile.mkdtemp()
        self.command = command.Command(self.parser.parse_args([]), tempdir)
        self.command._get_filename_key = MagicMock(return_value=0)

    def tearDown(self):
        shutil.rmtree(self.command.requirements_dir, ignore_errors=True)

    def test_get_filename(self):
        self.command._get_filename_key = MagicMock(side_effect=['a', 0])

        filename = self.command._get_filename('', ['test.text'], '')

        self.assertEqual('test.text', filename)

    def test_generate_requirements_files_no_data(self):
        self.command._get_installed_packages = MagicMock(return_value=set())

        self.command.generate_requirements_files()

        self.assertTrue(os.path.exists(self.command.requirements_dir))

    @patch('subprocess.check_output')
    def test_generate_requirements_files_create(self, mock_check_output):
        mock_check_output.return_value = 'mock==1.1\nflake8==2.5\n'

        self.command.generate_requirements_files()

        self.assertTrue(os.path.exists(self.command.requirements_dir))
        common_reqs = open(os.path.join(self.command.requirements_dir, 'requirements.txt'))
        self.assertEqual('flake8==2.5\nmock==1.1\n', common_reqs.read())

    @patch('subprocess.check_output')
    def test_generate_requirements_files_update(self, mock_check_output):
        mock_check_output.return_value = 'mock==1.1\nflake8==2.5\n'
        _create_requirements_file(self.command.requirements_dir, 'common.txt',
                                  'mock==1.2\nDjango==1.7\nnose==1.3\n')

        self.command.generate_requirements_files()

        self.assertTrue(os.path.exists(self.command.requirements_dir))
        common_reqs = open(os.path.join(self.command.requirements_dir, 'common.txt'))
        self.assertEqual('Django==1.7\nflake8==2.5\nmock==1.1\nnose==1.3\n', common_reqs.read())

    @patch('subprocess.check_output')
    def test_run_generate_requirements_files(self, mock_check_output):
        mock_check_output.return_value = 'mock==1.1\nflake8==2.5\n'
        _create_requirements_file(self.command.requirements_dir, 'common.txt',
                                  content='Django==1.7\n')
        vcs_line = ('-e git://github.com/jessamynsmith/django_coverage_plugin.git@'
                    'f03bdc0981ceface4bfea6aa3544e519a2b908aa#egg=django-coverage-plugin')
        uri_line = '-e http://example.com/some-repo.git'
        content = '-r common.txt\nmock==1.2\n%s\nnose==1.3\n%s\n' % (vcs_line, uri_line)
        _create_requirements_file(self.command.requirements_dir, 'development.txt', content=content)
        self.command.args = self.parser.parse_args(['-r'])

        self.command.run()

        self.assertTrue(os.path.exists(self.command.requirements_dir))
        common_reqs = open(os.path.join(self.command.requirements_dir, 'common.txt'))
        self.assertEqual('Django==1.7\nflake8==2.5\n', common_reqs.read())
        dev_reqs = open(os.path.join(self.command.requirements_dir, 'development.txt'))
        expected = '-r common.txt\n%s\n%s\nmock==1.1\nnose==1.3\n' % (vcs_line, uri_line)
        self.assertEqual(expected, dev_reqs.read())

    def test_run_invalid_option(self):
        result = self.command.run()

        self.assertEqual(1, result)


class TestRemoveExtra(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.parser = cli.create_parser()
        tempdir = tempfile.mkdtemp()
        self.command = command.Command(self.parser.parse_args([]), tempdir)

    def tearDown(self):
        shutil.rmtree(self.command.requirements_dir, ignore_errors=True)

    @patch('subprocess.check_output')
    @patch('subprocess.check_call')
    def test_remove_extra_packages_with_dashe_directive(self, mock_check_call, mock_check_output):
        mock_check_output.return_value = \
            'mock==1.2\nDjango==1.7\nnose==1.3\n' \
            '-e http://example.com/some-repo.git\n' \
            'django-nose==1.0\n'
        _create_requirements_file(self.command.requirements_dir,
                                  'mock==1.2\nDjango==1.7\nnose==1.3\n')

        extras = self.command._determine_extra_packages()

        extras = sorted(list(extras), key=get_key)
        self.assertEqual(2, len(extras))
        self.assertEqual("-e http://example.com/some-repo.git", extras[0].line)
        self.assertEqual("django-nose", extras[1].name)
        self.assertFalse(mock_check_call.called)

    @patch('subprocess.check_output')
    @patch('subprocess.check_call')
    def test_remove_extra_packages_when_none_to_remove(self, mock_check_call, mock_check_output):
        mock_check_output.return_value = 'mock==1.2\nDjango==1.7\nnose==1.3\n'
        _create_requirements_file(self.command.requirements_dir)

        self.command.remove_extra_packages()

        self.assertFalse(mock_check_call.called)

    @patch('subprocess.check_output')
    @patch('subprocess.check_call')
    def test_remove_extra_packages_when_some_to_remove(self, mock_check_call, mock_check_output):
        mock_check_output.return_value = 'mock==1.2\nDjango==1.7\nnose==1.3\ndjango-nose==1.0\n'
        _create_requirements_file(self.command.requirements_dir)

        self.command.remove_extra_packages()

        mock_check_call.assert_called_once_with(['pip', 'uninstall', '-y', 'django-nose'])

    @patch('subprocess.check_output')
    @patch('subprocess.check_call')
    def test_run_remove_extra_packages_dry_run(self, mock_check_call, mock_check_output):
        mock_check_output.return_value = 'mock==1.2\nDjango==1.7\nnose==1.3\ndjango-nose==1.0\n'
        _create_requirements_file(self.command.requirements_dir)
        self.command.args = self.parser.parse_args(['-xn'])

        self.command.run()

        expected = "The following packages would be removed:\n    django-nose"
        self.assertEqual(expected, sys.stdout.getvalue().strip())
        self.assertFalse(mock_check_call.called)

    @patch('subprocess.check_output')
    @patch('subprocess.check_call')
    def test_run_remove_extra_packages(self, mock_check_call, mock_check_output):
        mock_check_output.return_value = 'mock==1.2\nDjango==1.7\nnose==1.3\ndjango-nose==1.0\n'
        _create_requirements_file(self.command.requirements_dir)
        self.command.args = self.parser.parse_args(['-x'])

        self.command.run()

        mock_check_call.assert_called_once_with(['pip', 'uninstall', '-y', 'django-nose'])
