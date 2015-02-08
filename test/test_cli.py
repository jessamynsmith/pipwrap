from mock import patch
import sys
import tempfile
import unittest

from pipreq import cli


class TestCli(unittest.TestCase):

    def setUp(self):
        self.parser = cli.create_parser()

    def test_verify_args_no_args(self):
        args = self.parser.parse_args([])

        error_message = cli.verify_args(args)

        expected_error = ('Must specify generate (-g) or create/upgrade/remove-missing (-[cur]) '
                          'with packages')
        self.assertEqual(expected_error, error_message)

    def test_verify_args_create_with_packages(self):
        package_file = tempfile.NamedTemporaryFile()

        args = self.parser.parse_args(['-c', package_file.name])

        error_message = cli.verify_args(args)

        self.assertEqual(None, error_message)

    def test_verify_args_generate(self):
        args = self.parser.parse_args(['-g'])

        error_message = cli.verify_args(args)

        self.assertEqual(None, error_message)

    @patch('argparse.ArgumentParser.exit')
    def test_error(self, mock_exit):
        cli.error(self.parser, 'An error occurred!')

        mock_exit.assert_called_once_with(message='\nERROR: An error occurred!\n')

    def test_main_no_args(self):
        try:
            cli.main()
            self.fail("Should fail without arguments")
        except SystemExit as e:
            self.assertEqual('0', str(e))

    def test_main_invalid_args(self):
        sys.argv = ['pipreq', '-c', '-g']

        try:
            cli.main()
            self.fail("Should fail with invalid argument")
        except SystemExit as e:
            self.assertEqual('0', str(e))

    def test_main_success(self):
        _, packages = tempfile.mkstemp()
        sys.argv = ['pipreq', '-U', packages]

        result = cli.main()

        self.assertEqual(0, result)
