from mock import patch
import sys
import tempfile
import unittest

from pipreq import cli


class MockPackage():
    def __init__(self):
        self.version = 0.4


class TestCli(unittest.TestCase):

    def setUp(self):
        self.parser = cli.create_parser()

    def test_verify_args_no_args(self):
        args = self.parser.parse_args([])

        error_message = cli.verify_args(args)

        expected_error = ('Must specify generate (-g) or create/upgrade/remove-missing (-[cUx]) '
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

    def test_verify_args_remove_extra_dry_run(self):
        args = self.parser.parse_args(['-x', '-n'])

        error_message = cli.verify_args(args)

        self.assertEqual(None, error_message)

    def test_verify_args_update_dry_run(self):
        args = self.parser.parse_args(['-U', '-n'])

        error_message = cli.verify_args(args)

        expected_error = "-n is only supported with -x"
        self.assertEqual(expected_error, error_message)

    @patch('argparse.ArgumentParser.exit')
    def test_error(self, mock_exit):
        cli.error(self.parser, 'An error occurred!')

        mock_exit.assert_called_once_with(message='\nERROR: An error occurred!\n')

    def test_main_no_args(self):
        sys.argv = ['pipreq']
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

    @patch('pkg_resources.require')
    def test_main_version(self, mock_require):
        sys.argv = ['pipreq', '--version']
        mock_require.return_value = [MockPackage()]

        try:
            cli.main()
            self.fail("Should exit on version request")
        except SystemExit as e:
            self.assertEqual('pipreq 0.4', '{0}'.format(e))
        mock_require.assert_called_once_with('pipreq')

    def test_main_success(self):
        _, packages = tempfile.mkstemp()
        sys.argv = ['pipreq', '-U', packages]

        result = cli.main()

        self.assertEqual(0, result)

    @patch('argparse.ArgumentParser')
    def test_main_keyboard_interrupt(self, mock_argparse):
        sys.argv = ['pipreq', '--version']
        mock_argparse.side_effect = KeyboardInterrupt()

        try:
            cli.main()
            self.fail("Should exit on version request")
        except SystemExit as e:
            self.assertEqual('', '{0}'.format(e))
