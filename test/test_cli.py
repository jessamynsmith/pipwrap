from mock import patch
import sys
import unittest

from pipwrap import cli


class MockPackage():
    def __init__(self):
        self.version = 0.4


class TestCli(unittest.TestCase):

    def setUp(self):
        self.parser = cli.create_parser()

    def test_verify_args_no_args(self):
        args = self.parser.parse_args([])

        error_message = cli.verify_args(args)

        expected_error = ('Must specify --requirements-files (-r) or --remove-missing (-x) '
                          'or --lint (-l).')
        self.assertEqual(expected_error, error_message)

    def test_verify_args_generate(self):
        args = self.parser.parse_args(['-r'])

        error_message = cli.verify_args(args)

        self.assertEqual(None, error_message)

    def test_verify_args_lint(self):
        args = self.parser.parse_args(['-l'])

        error_message = cli.verify_args(args)

        self.assertEqual(None, error_message)

    def test_verify_args_remove_extra(self):
        args = self.parser.parse_args(['-x'])

        error_message = cli.verify_args(args)

        self.assertEqual(None, error_message)

    def test_verify_args_remove_extra_clean(self):
        args = self.parser.parse_args(['-x', '-c'])

        error_message = cli.verify_args(args)

        expected_error = "-c is only supported with -r"
        self.assertEqual(expected_error, error_message)

    @patch('argparse.ArgumentParser.exit')
    def test_error(self, mock_exit):
        cli.error(self.parser, 'An error occurred!')

        mock_exit.assert_called_once_with(message='\nERROR: An error occurred!\n')

    def test_main_no_args(self):
        sys.argv = ['pipwrap']
        try:
            cli.main()
            self.fail("Should fail without arguments")
        except SystemExit as e:
            self.assertEqual('0', str(e))

    def test_main_invalid_args(self):
        sys.argv = ['pipwrap', '-x', '-r']

        try:
            cli.main()
            self.fail("Should fail with invalid argument")
        except SystemExit as e:
            self.assertEqual('0', str(e))

    @patch('pkg_resources.require')
    def test_main_version(self, mock_require):
        sys.argv = ['pipwrap', '--version']
        mock_require.return_value = [MockPackage()]

        try:
            cli.main()
            self.fail("Should exit on version request")
        except SystemExit as e:
            self.assertEqual('pipwrap 0.4', '{0}'.format(e))
        mock_require.assert_called_once_with('pipwrap')

    @patch('pipwrap.command.Command.run')
    def test_main_success(self, mock_run):
        mock_run.return_value = 1
        sys.argv = ['pipwrap', '-l']

        result = cli.main()

        self.assertEqual(1, result)

    @patch('argparse.ArgumentParser')
    def test_main_keyboard_interrupt(self, mock_argparse):
        sys.argv = ['pipwrap', '--version']
        mock_argparse.side_effect = KeyboardInterrupt()

        try:
            cli.main()
            self.fail("Should exit on version request")
        except SystemExit as e:
            self.assertEqual('', '{0}'.format(e))
