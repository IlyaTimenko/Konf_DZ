import unittest
from unittest.mock import patch
from io import StringIO
from path.to.your.config_converter import ConfigConverter

class TestConfigConverter(unittest.TestCase):

    @patch('sys.stdin', new_callable=StringIO)
    @patch('builtins.print')
    def test_parse_toml_declaration(self, mock_print, mock_stdin):
        mock_stdin.write('myVar = "Hello"\n')
        mock_stdin.write('myArray = (1, 2, 3)\n')
        mock_stdin.write('myConst = @myVar\n')
        mock_stdin.write('myUnusedVar = @notExisting\n')
        mock_stdin.write('myErrVar = invalid\n')
        mock_stdin.seek(0)

        converter = ConfigConverter()
        converter.convert()

        mock_print.assert_any_call('var myVar := Hello')
        mock_print.assert_any_call('var myArray := [1, 2, 3]')
        mock_print.assert_any_call('Hello')
        mock_print.assert_any_call("Ошибка: Константа 'notExisting' не объявлена.")
        mock_print.assert_any_call("Ошибка: Неправильный синтаксис: 'myErrVar = invalid'")

if __name__ == '__main__':
    unittest.main()