import unittest
from unittest.mock import patch, MagicMock
from path.to.your.shell_emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    @patch('aspose.zip.tar.TarArchive', new_callable=MagicMock)
    def setUp(self, mock_tar):
        self.emulator = ShellEmulator('mocked_fs.tar')
        self.emulator.tar_archive.entries = [
            MagicMock(name='entry1', name='file1.txt', length=100),
            MagicMock(name='entry2', name='dir1/file2.txt', length=200),
            MagicMock(name='entry3', name='dir1/subdir3/file3.txt', length=150)
        ]

    def test_ls(self):
        result = self.emulator.ls()
        self.assertIn('file1.txt', result)
        self.assertIn('dir1', result)

    def test_cd_valid(self):
        result = self.emulator.cd(['dir1'])
        self.assertEqual(self.emulator.current_path, Path('dir1'))
        self.assertEqual(result, '')

    def test_cd_invalid(self):
        result = self.emulator.cd(['nonexistent_dir'])
        self.assertEqual(result, 'Ошибка: путь nonexistent_dir не найден.')

    def test_rmdir_valid(self):
        result = self.emulator.rmdir(['dir1'])
        self.assertIn('Директория dir1 и её содержимое удалены.', result)

    def test_rmdir_invalid(self):
        result = self.emulator.rmdir(['nonexistent_dir'])
        self.assertEqual(result, 'Ошибка: директория nonexistent_dir не найдена.')

    def test_du_valid(self):
        result = self.emulator.du(['dir1'])
        self.assertIn('Размер директории dir1:', result)

    def test_du_invalid(self):
        result = self.emulator.du(['nonexistent_dir'])
        self.assertEqual(result, 'Ошибка: путь nonexistent_dir не найден.')

if __name__ == '__main__':
    unittest.main()