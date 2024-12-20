import aspose.zip.tar as tar
from pathlib import Path
import tkinter as tk

class ShellEmulator:
    def __init__(self, fs_path, username="user", hostname="host"):
        self.current_path = Path("/")
        self.fs_path = fs_path
        self.username = username
        self.hostname = hostname
        self.load_filesystem()

    def load_filesystem(self):
        if not Path(self.fs_path).exists():
            raise FileNotFoundError("Файл виртуальной файловой системы не найден.")
        self.tar_archive = tar.TarArchive(self.fs_path)

    def list_dir(self, path):
        self.load_filesystem()
        path = str(path).lstrip("/")
        if path and not path.endswith("/"):
            path += "/"
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
        files_in_dir = [entry for entry in self.tar_archive.entries if entry.name.startswith(dir_path)]
        if not files_in_dir:
            return f"Ошибка: директория {args[0]} не найдена."
        with tar.TarArchive(self.fs_path) as archive:
            for file in files_in_dir:
                archive.delete_entry(file)
            archive.save(self.fs_path[2:], tar.TarFormat.US_TAR)
        return f"Директория {args[0]} и её содержимое удалены.\n{self.ls()}"

    def du(self, args):
        if not args:
            return "Ошибка: отсутствует аргумент для du."
        dir_path = str(self.current_path / args[0]).lstrip("/")
        files_in_dir = [entry for entry in self.tar_archive.entries if entry.name.startswith(dir_path)]
        if not files_in_dir:
            return f"Ошибка: путь {args[0]} не найден."
        size = sum(entry.length for entry in files_in_dir)
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