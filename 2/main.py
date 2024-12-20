import subprocess
import os
import sys

class DependencyVisualizer:
    def __init__(self, plantuml_path, package_name, output_image_path, repo_url):
        self.plantuml_path = plantuml_path
        self.package_name = package_name
        self.output_image_path = output_image_path
        self.repo_url = repo_url

    def get_dependencies(self):
        command = f"apt-cache depends {self.package_name}"
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return result.decode("utf-8")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при получении зависимостей для {self.package_name}: {e.output.decode('utf-8')}")
            return None

    def sanitize_dependency(self, dep):
        dep = dep.replace("<", "_LT_").replace(">", "_GT_").replace(":", "_COLON_")
        return dep

    def generate_puml(self, dependencies):
        puml_lines = ["@startuml"]
        visited = set()
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
        puml_file_path = "temp_graph.puml"
        with open(puml_file_path, "w") as f:
            f.write(puml_content)
        return puml_file_path

    def generate_graph(self, puml_file):
        try:
            command = f"java -jar {self.plantuml_path} {puml_file}"
            subprocess.check_call(command, shell=True)
            print(f"Граф успешно создан и сохранён как {self.output_image_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при генерации PNG: {e}")
            return False
        return True

    def visualize(self):
        dependencies = self.get_dependencies()
        if dependencies is None:
            print("Ошибка при получении зависимостей.")
            return

        puml_content = self.generate_puml(dependencies)
        puml_file = self.create_puml_file(puml_content)

        if self.generate_graph(puml_file):
            os.rename("temp_graph.png", self.output_image_path)