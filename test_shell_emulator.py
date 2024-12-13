import unittest
import os
import zipfile
import shutil
from tkinter import Tk
from ShellEmulator import ShellEmulator  # Импортируйте ваш эмулятор

class TestShellEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Создаем временный ZIP-архив для тестов
        cls.vfs_zip_path = "test_vfs.zip"
        cls.setup_test_vfs()

    @classmethod
    def tearDownClass(cls):
        # Удаляем временные файлы и директории
        if os.path.exists(cls.vfs_zip_path):
            os.remove(cls.vfs_zip_path)
        if os.path.exists("vfs"):
            shutil.rmtree("vfs")

    @classmethod
    def setup_test_vfs(cls):
        # Создаем тестовую файловую систему
        os.makedirs("test_vfs/test_dir", exist_ok=True)
        with open("test_vfs/test_file.txt", "w") as f:
            f.write("This is a test file.")
        with open("test_vfs/test_dir/another_file.txt", "w") as f:
            f.write("This is another test file.")

        # Создание zip-архива
        with zipfile.ZipFile(cls.vfs_zip_path, "w") as zipf:
            for root, _, files in os.walk("test_vfs"):
                for file in files:
                    zipf.write(os.path.join(root, file),
                                os.path.relpath(os.path.join(root, file), os.path.join("test_vfs", '..')))
        shutil.rmtree("test_vfs")  # Удалить исходные тестовые файлы

    def setUp(self):
        # Создаем экземпляр ShellEmulator для тестов
        self.root = Tk()  # Создаем корневой элемент Tkinter
        self.emulator = ShellEmulator(self.root, "test_user", "test_host", self.vfs_zip_path)

    def tearDown(self):
        self.root.destroy()  # Уничтожаем элемент Tkinter после теста

    def test_initial_directory(self):
        self.assertEqual(self.emulator.get_current_directory(), "", "Initial directory should be empty.")

    def test_ls_command(self):
        # Проверяем, что команда ls выводит файлы
        self.emulator.list_dir()
        output = self.emulator.text_area.get("1.0", "end-1c")
        self.assertIn("test_file.txt", output, "test_file.txt should be listed.")
        self.assertIn("test_dir", output, "test_dir should be listed.")

    def test_cd_command(self):
        # Проверяем переход в директорию test_dir
        self.emulator.change_dir("test_dir")
        self.assertEqual(self.emulator.get_current_directory(), "test_dir", "Current directory should be test_dir after cd.")

        # Проверяем переход обратно
        self.emulator.change_dir("..")
        self.assertEqual(self.emulator.get_current_directory(), "", "Current directory should be empty after going back to root.")

    def test_invalid_cd_command(self):
        # Проверяем случай, когда пытаемся перейти в несуществующую директорию
        self.emulator.change_dir("invalid_dir")
        self.assertEqual(self.emulator.get_current_directory(), "", "Current directory should remain empty.")
        output = self.emulator.text_area.get("1.0", "end-1c")
        self.assertIn("No such directory", output, "Error message for invalid directory should be shown.")

    def test_rev_command(self):
        # Проверяем, что команда rev выводит всю историю в обратном порядке
        self.emulator.history = ["command1", "command2", "command3"]
        self.emulator.reverse_history()
        output = self.emulator.text_area.get("1.0", "end-1c")
        self.assertIn("command3", output, "History should include command3.")
        self.assertIn("command2", output, "History should include command2.")
        self.assertIn("command1", output, "History should include command1.")

    def test_history_command(self):
        # Проверяем, что команда history выводит всю историю
        self.emulator.history = ["command1", "command2"]
        self.emulator.show_history()
        output = self.emulator.text_area.get("1.0", "end-1c")
        self.assertIn("command1", output, "History should include command1.")
        self.assertIn("command2", output, "History should include command2.")

    def test_ls_empty_directory(self):
        # Проверяем ls в пустой директории
        self.emulator.change_dir("test_dir")  # Переходим в test_dir
        self.emulator.change_dir("new_dir")  # пробуем перейти в несуществующую папку
        self.emulator.list_dir()  # Вызываем ls для  пустой директории
        output = self.emulator.text_area.get("1.0", "end-1c")
        self.assertIn("No files or directories found.", output, "Should indicate no files in the directory.")

    def test_root_directory_listing(self):
        # Проверяем, что корневой каталог показывает файлы и директории
        self.emulator.list_dir()
        output = self.emulator.text_area.get("1.0", "end-1c")
        self.assertIn("test_file.txt", output, "Root directory should show test_file.txt.")
        self.assertIn("test_dir", output, "Root directory should show test_dir.")

if __name__ == "__main__":
    unittest.main()
