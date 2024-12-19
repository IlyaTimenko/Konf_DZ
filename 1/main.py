import aspose.zip.tar as tar
from pathlib import Path
from tkinter import messagebox
import tkinter as tk


class ShellEmulator:
    def __init__(self, fs_path, username="user", hostname="host"):
        self.current_path = Path("/")
        self.fs_path = fs_path  # Путь к архиву
        self.username = username  # Имя пользователя по умолчанию
        self.hostname = hostname  # Имя устройства по умолчанию
        self.load_filesystem()

    def load_filesystem(self):
        # Загружаем архив с помощью Aspose.Zip
        if not Path(self.fs_path).exists():
            raise FileNotFoundError("Файл виртуальной файловой системы не найден.")
        
        self.tar_archive = tar.TarArchive(self.fs_path)

    def list_dir(self, path):
        self.load_filesystem()
        
        path = str(path).lstrip("/")
        if path and not path.endswith("/"):
            path += "/"

        # Получаем имена всех файлов и директорий в архиве
        return sorted(
            {
                entry.name[len(path):].split("/", 1)[0]
                for entry in self.tar_archive.entries
                if entry.name.startswith(path) and entry.name != path
            }
        )
        

    def ls(self):
        try:
            items = self.list_dir(self.current_path)
            return "\n".join(items)
        except Exception as e:
            return f"Ошибка: {str(e)}"

    def cd(self, args):
        if not args:
            return "Ошибка: отсутствует аргумент для cd."

        if args[0] == "..":
            if self.current_path == Path("/"):
                return "Ошибка: вы не можете выйти за пределы виртуальной файловой системы."
            self.current_path = self.current_path.parent
        else:
            target_path = (self.current_path / args[0]).resolve()
            target_path_str = str(target_path).lstrip("/") + "/"

            if not any(entry.name.startswith(target_path_str) for entry in self.tar_archive.entries):
                return f"Ошибка: путь {args[0]} не найден."

            self.current_path = target_path
        return ""

    def rmdir(self, args):
        if not args:
            return "Ошибка: отсутствует аргумент для rmdir."

        dir_path = str(self.current_path / args[0]).lstrip("/") + "/"

        # Проверка, существует ли директория в архиве
        files_in_dir = [entry for entry in self.tar_archive.entries if entry.name.startswith(dir_path)]

        if not files_in_dir:
            return f"Ошибка: директория {args[0]} не найдена."
        
        # Удаление всех файлов внутри директории
        with tar.TarArchive(self.fs_path) as archive:
            
            for file in files_in_dir:
                archive.delete_entry(file)
            
            # Сохраняем изменения в архиве
            archive.save(self.fs_path[2:], tar.TarFormat.US_TAR)

        return f"Директория {args[0]} и её содержимое удалены.\n{self.ls()}"

    def du(self, args):
        if not args:
            return "Ошибка: отсутствует аргумент для du."

        dir_path = str(self.current_path / args[0]).lstrip("/")
        files_in_dir = [entry for entry in self.tar_archive.entries if entry.name.startswith(dir_path)]

        if not files_in_dir:
            return f"Ошибка: путь {args[0]} не найден."

        size = 0
        for entry in files_in_dir:
            size += entry.length # Используем uncompressed_size для получения размера данных

        return f"Размер директории {args[0]}: {size} байт."

    def run_command(self, command):
        parts = command.strip().split()
        if not parts:
            return ""

        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            return self.ls()
        elif cmd == "cd":
            return self.cd(args)
        elif cmd == "exit":
            exit(0)
        elif cmd == "rmdir":
            return self.rmdir(args)
        elif cmd == "du":
            return self.du(args)
        else:
            return f"Команда {cmd} не найдена."


class ShellGUI:
    def __init__(self, emulator):
        self.emulator = emulator
        self.window = tk.Tk()
        self.window.title("Shell Emulator")
        self.window.configure(bg="black")
        self.window.geometry("800x600")  # Устанавливаем размер окна

        self.output = tk.Text(self.window, wrap=tk.WORD, state=tk.DISABLED, height=30, width=100,
                              bg="black", fg="white", font=("Courier", 12), insertbackground="white")
        self.output.pack(padx=10, pady=10)

        self.input_field = tk.Entry(self.window, width=100, font=("Courier", 12), bg="black", fg="white", insertbackground="white")
        self.input_field.pack(padx=10, pady=10)
        self.input_field.bind("<Return>", self.execute_command)

    def execute_command(self, event):
        command = self.input_field.get()
        if command:
            prompt = f"{self.emulator.username}@{self.emulator.hostname}:{self.emulator.current_path}$ {command}\n"
            result = self.emulator.run_command(command)
            self.append_output(prompt + (result or "") + "\n")
            self.input_field.delete(0, tk.END)

    def append_output(self, text):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, text)
        self.output.config(state=tk.DISABLED)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        messagebox.showerror("Ошибка", "Необходимо указать путь к архиву виртуальной файловой системы.")
        exit(1)

    fs_path = sys.argv[1]

    username = "user"
    hostname = "host"

    try:
        emulator = ShellEmulator(fs_path, username, hostname)
        gui = ShellGUI(emulator)
        gui.run()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
