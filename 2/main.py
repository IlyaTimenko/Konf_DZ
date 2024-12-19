import subprocess
import os
import sys
from pathlib import Path

class DependencyVisualizer:
    def __init__(self, plantuml_path, package_name, output_image_path, repo_url):
        self.plantuml_path = plantuml_path
        self.package_name = package_name
        self.output_image_path = output_image_path
        self.repo_url = repo_url

    def get_dependencies(self):
        # Получаем зависимости для пакета через apt-cache (Ubuntu)
        command = f"apt-cache depends {self.package_name}"
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при получении зависимостей для {self.package_name}: {e.output.decode('utf-8')}")
            return None

    def sanitize_dependency(self, dep):
        """Экранирует или заменяет опасные символы в именах зависимостей"""
        # Заменяем опасные символы на безопасные
        dep = dep.replace("<", "_LT_").replace(">", "_GT_").replace(":", "_COLON_")
        return dep

    def generate_puml(self, dependencies):
        """Генерирует строку для файла PlantUML, экранируя ошибки и зависимости"""
        puml_lines = ["@startuml"]
        visited = set()

        # Для каждой зависимости генерируем соответствующие записи в PlantUML
        for line in dependencies.splitlines():
            if line.startswith("  Depends:"):
                dep_name = line.split(":")[1].strip()
                dep_name = self.sanitize_dependency(dep_name)
                if dep_name not in visited:
                    puml_lines.append(f'"{self.package_name}" --> "{dep_name}"')
                    visited.add(dep_name)
        
        puml_lines.append("@enduml")
        return "\n".join(puml_lines)

    def create_puml_file(self, puml_content):
        """Создаёт временный puml файл для дальнейшей обработки"""
        puml_file_path = "temp_graph.puml"
        with open(puml_file_path, "w") as f:
            f.write(puml_content)
        return puml_file_path

    def generate_graph(self, puml_file):
        """Создаёт граф из puml файла с использованием PlantUML"""
        try:
            command = f"java -jar {self.plantuml_path} {puml_file}"
            subprocess.check_call(command, shell=True)
            print(f"Граф успешно создан и сохранён как {self.output_image_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при генерации PNG: {e}")
            return False
        return True

    def visualize(self):
        """Главный метод для генерации графа зависимостей"""
        dependencies = self.get_dependencies()
        if dependencies is None:
            print("Ошибка при получении зависимостей.")
            return

        puml_content = self.generate_puml(dependencies)
        puml_file = self.create_puml_file(puml_content)

        if self.generate_graph(puml_file):
            # Перемещаем изображение в нужное место
            os.rename("temp_graph.png", self.output_image_path)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Ошибка: Необходимо указать все параметры командной строки.")
        sys.exit(1)

    plantuml_path = sys.argv[1]  # Путь к PlantUML jar
    package_name = sys.argv[2]   # Имя пакета для анализа
    output_image_path = sys.argv[3]  # Путь для сохранения изображения
    repo_url = sys.argv[4]  # URL репозитория (не используется в данном примере, но может быть полезен)

    visualizer = DependencyVisualizer(plantuml_path, package_name, output_image_path, repo_url)
    visualizer.visualize()