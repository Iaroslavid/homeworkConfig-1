import tkinter as tk
from tkinter import scrolledtext
import sys
import zipfile
import os

class ShellEmulator:
    def __init__(self, master, username, hostname, vfs_path):
        self.master = master
        self.username = username
        self.hostname = hostname
        self.vfs_path = vfs_path
        self.history = []
        self.current_dir = ""  # Начнем с корня виртуальной файловой системы
        self.file_system = self.load_vfs()

        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(pady=10)

        self.input_area = tk.Entry(master, width=80)
        self.input_area.pack(pady=10)
        self.input_area.bind("<Return>", self.process_command)
        self.prompt()

    def load_vfs(self):
        with zipfile.ZipFile(self.vfs_path, 'r') as zip_ref:
            zip_ref.extractall("vfs")
        
        fs = {}
        self._build_file_system("vfs", fs)
        return fs

    def _build_file_system(self, path, fs_dict):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                # Добавляем директорию
                fs_dict[item] = {}
                self._build_file_system(item_path, fs_dict[item])
            else:
                # Добавляем файл
                fs_dict[item] = None  # обозначаем файл без вложенной структуры


    def prompt(self):
        self.input_area.delete(0, tk.END)
        self.text_area.insert(tk.END, f"{self.username}@{self.hostname}:{self.current_dir}$ ")
        self.text_area.see(tk.END)

    def process_command(self, event):
        command = self.input_area.get().strip()
        if command:
            self.history.append(command)
            self.text_area.insert(tk.END, f"{command}\n")

            if command.startswith("ls"):
                self.list_dir()
            elif command.startswith("cd "):
                self.change_dir(command[3:])
            elif command == "exit":
                self.master.quit()
            elif command == "rev":
                self.reverse_history()
            elif command == "history":
                self.show_history()
            else:
                self.text_area.insert(tk.END, "Command not found\n")

        self.prompt()

    def list_dir(self):
        current_files = self.get_current_files()
        self.text_area.insert(tk.END, f"Current directory: {self.current_dir}\n")
        self.text_area.insert(tk.END, f"Available files: {current_files}\n")  # Для отладки

        if current_files:
            self.text_area.insert(tk.END, "\n".join(current_files) + "\n")
        else:
            self.text_area.insert(tk.END, "No files or directories found.\n")

    def get_current_files(self):
        dirs = self.current_dir.split('/')
        fs_level = self.file_system
        for d in dirs:
            if d:  # пропускаем пустые элементы
                fs_level = fs_level.get(d, {})
        return [f for f in fs_level.keys()]



    def change_dir(self, dir_name):
        if dir_name in self.get_current_files():
            # Меняем директорию
            self.current_dir = os.path.join(self.current_dir, dir_name)
        elif dir_name == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        else:
            self.text_area.insert(tk.END, "No such directory\n")


    def reverse_history(self):
        self.text_area.insert(tk.END, "\n".join(reversed(self.history)) + "\n")

    def show_history(self):
        self.text_area.insert(tk.END, "\n".join(self.history) + "\n")

    def get_current_directory(self):
        return self.current_dir

    def get_command_history(self):
        return self.history


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <username> <hostname> <vfs_zip_path>")
        sys.exit(1)

    username = sys.argv[1]
    hostname = sys.argv[2]
    vfs_zip_path = sys.argv[3]

    root = tk.Tk()
    app = ShellEmulator(root, username, hostname, vfs_zip_path)
    root.mainloop()
