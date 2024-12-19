import sys
import re

class ConfigConverter:
    def __init__(self):
        self.constants = {}

    def parse_toml(self, line):
        # Удаляем однострочные комментарии
        comment_match = re.search(r'#.*$', line)
        if comment_match:
            comment = comment_match.group(0)[1:].strip()  # Убираем символ # и пробелы
            print(f"*> {comment}")  # Выводим комментарий в нужном формате
            line = line[:comment_match.start()].strip()
        else:
            line = line.strip()
        
        if not line:
            return
        
        # Обработка объявления константы
        match = re.match(r'(\w+)\s*=\s*(.+)', line)
        if match:
            name, value = match.groups()
            self.constants[name] = self.parse_value(value)
            print(f"var {name} := {self.constants[name]}")  # Выводим объявление константы
            return
        
        # Обработка вычисления константы
        match = re.match(r'@(\w+)', line)
        if match:
            name = match.group(1)
            if name in self.constants:
                print(self.constants[name])  # Выводим значение константы
            else:
                print(f"Ошибка: Константа '{name}' не объявлена.")
            return
        
        print(f"Ошибка: Неправильный синтаксис: '{line}'")

    def parse_value(self, value):
        # Обработка массивов
        if value.startswith('(') and value.endswith(')'):
            array_values = value[1:-1].split(',')
            return [self.parse_value(v.strip()) for v in array_values]
        
        # Обработка чисел
        try:
            return int(value)
        except ValueError:
            return value.strip('"')

    def convert(self):
        for line in sys.stdin:
            self.parse_toml(line)

if __name__ == "__main__":
    converter = ConfigConverter()
    converter.convert()
