import os
import StringIO
import tempfile
import unittest

from pipreq import cli, command


class TestCommand(unittest.TestCase):

    def setUp(self):
        self.parser = cli.create_parser()
        rc_file = tempfile.NamedTemporaryFile()
        self.blank_command = command.Command(self.parser.parse_args([]), rc_file.name)

        rc_file = tempfile.NamedTemporaryFile()
        rc_file.write('[metadata]\nshared=common\n[development]\nmock=1.0\n'
                      '[common]\nDjango=1.7\npsycopg2=2.5.4\n')
        rc_file.flush()
        self.populated_command = command.Command(self.parser.parse_args([]), rc_file.name)

    def test_init(self):
        self.assertTrue(self.populated_command.config.has_section('common'))
        self.assertTrue(self.populated_command.config.has_option('common', 'Django'))

        # Ensure that capitalization is preserved
        output = StringIO.StringIO()
        self.populated_command.config.write(output)
        expected = ('[metadata]\nshared = common\n\n[development]\nmock = 1.0\n\n'
                    '[common]\nDjango = 1.7\npsycopg2 = 2.5.4\n\n')
        self.assertEqual(expected, output.getvalue())

    def test_add_section_new_section(self):
        self.blank_command._add_section('common')

        self.assertTrue(self.blank_command.config.has_section('common'))

    def test_add_section_duplicate_section(self):
        self.populated_command._add_section('common')

        self.assertTrue(self.populated_command.config.has_section('common'))

    def test_set_option(self):
        self.blank_command._set_option('common', 'Django', '1.7')

        self.assertTrue(self.blank_command.config.has_section('common'))
        self.assertTrue(self.blank_command.config.has_option('common', 'Django'))
        self.assertEqual('1.7', self.blank_command.config.get('common', 'Django'))

    def test_get_option_does_not_exist(self):
        section, value = self.blank_command._get_option('Django')

        self.assertEqual(None, section)
        self.assertEqual(None, value)

    def test_get_option_exists(self):
        section, value = self.populated_command._get_option('Django')

        self.assertEqual('common', section)
        self.assertEqual('1.7', value)

    def test_get_shared_section_does_not_exist(self):
        shared = self.blank_command._get_shared_section()

        self.assertEqual(None, shared)

    def test_get_shared_section_exists(self):
        shared = self.populated_command._get_shared_section()

        self.assertEqual('common', shared)

    def test_make_requirements_directory_does_not_exist(self):
        tempdir = tempfile.mkdtemp()

        req_dir = self.blank_command._make_requirements_directory(tempdir)

        self.assertEqual('%s/requirements' % tempdir, req_dir)

    def test_make_requirements_directory_exists(self):
        tempdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tempdir, 'requirements'))

        req_dir = self.blank_command._make_requirements_directory(tempdir)

        self.assertEqual(os.path.join(tempdir, 'requirements'), req_dir)

    def test_format_requirements_line(self):
        line = self.blank_command._format_requirements_line('Django', '1.7')

        self.assertEqual('Django==1.7\n', line)

    def test_write_requirements_file_for_shared_section(self):
        req_file = tempfile.NamedTemporaryFile()
        reqs = {'Django': '1.7', 'psycopg2': '2.5.4'}

        self.blank_command._write_requirements_file('common', 'common', reqs, req_file.name)

        self.assertEqual('Django==1.7\npsycopg2==2.5.4\n', req_file.read())

    def test_write_requirements_file_with_shared_section(self):
        req_file = tempfile.NamedTemporaryFile()
        reqs = {'gunicorn': '19.1.1'}

        self.blank_command._write_requirements_file('common', 'production', reqs, req_file.name)

        self.assertEqual('-r common.txt\ngunicorn==19.1.1\n', req_file.read())

    def test_generate_requirements_files_no_data(self):
        tempdir = tempfile.mkdtemp()

        self.blank_command.generate_requirements_files(tempdir)

        self.assertTrue(os.path.exists(os.path.join(tempdir, 'requirements')))

    def test_generate_requirements_files_with_data(self):
        tempdir = tempfile.mkdtemp()
        self.populated_command.config.add_section('empty')

        self.populated_command.generate_requirements_files(tempdir)

        self.assertTrue(os.path.exists(os.path.join(tempdir, 'requirements')))
        common_reqs = open(os.path.join(tempdir, 'requirements', 'common.txt'))
        self.assertEqual('Django==1.7\npsycopg2==2.5.4\n', common_reqs.read())
        dev_reqs = open(os.path.join(tempdir, 'requirements', 'development.txt'))
        self.assertEqual('-r common.txt\nmock==1.0\n', dev_reqs.read())
