import sys
import re

class ConfigConverter:
    def __init__(self):
        self.constants = {}

    def parse_toml(self, line):
        comment_match = re.search(r'#.*$', line)
        if comment_match:
            comment = comment_match.group(0)[1:].strip()
            print(f"*> {comment}")
            line = line[:comment_match.start()].strip()
        else:
            line = line.strip()
        
        if not line:
            return
        
        match = re.match(r'(\w+)\s*=\s*(.+)', line)
        if match:
            name, value = match.groups()
            self.constants[name] = self.parse_value(value)
            print(f"var {name} := {self.constants[name]}")
            return
        
        match = re.match(r'@(\w+)', line)
        if match:
            name = match.group(1)
            if name in self.constants:
                print(self.constants[name])
            else:
                print(f"Ошибка: Константа '{name}' не объявлена.")
            return
        
        print(f"Ошибка: Неправильный синтаксис: '{line}'")

    def parse_value(self, value):
        if value.startswith('(') and value.endswith(')'):
            array_values = value[1:-1].split(',')
            return [self.parse_value(v.strip()) for v in array_values]
        
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