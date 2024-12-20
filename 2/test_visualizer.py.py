import unittest
from unittest.mock import patch, MagicMock
from path.to.your.dependency_visualizer import DependencyVisualizer

class TestDependencyVisualizer(unittest.TestCase):
    
    @patch('subprocess.check_output')
    def test_get_dependencies_success(self, mock_check_output):
        mock_check_output.return_value = b"  Depends: package1\n  Depends: package2\n"
        visualizer = DependencyVisualizer("mock_plantuml.jar", "test_package", "output.png", "repo_url")
        dependencies = visualizer.get_dependencies()
        self.assertIn('package1', dependencies)
        self.assertIn('package2', dependencies)

    @patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'cmd', output=b'Error'))
    def test_get_dependencies_failure(self, mock_check_output):
        visualizer = DependencyVisualizer("mock_plantuml.jar", "test_package", "output.png", "repo_url")
        result = visualizer.get_dependencies()
        self.assertIsNone(result)

    def test_sanitize_dependency(self):
        visualizer = DependencyVisualizer("mock_plantuml.jar", "test_package", "output.png", "repo_url")
        sanitized = visualizer.sanitize_dependency("<dangerous:dependency>")
        self.assertEqual(sanitized, "_LT_dangerous_COLON_dependency_")

    def test_generate_puml(self):
        visualizer = DependencyVisualizer("mock_plantuml.jar", "test_package", "output.png", "repo_url")
        dependencies = "  Depends: package1\n  Depends: package2\n"
        puml_content = visualizer.generate_puml(dependencies)
        self.assertIn('"test_package" --> "package1"', puml_content)
        self.assertIn('"test_package" --> "package2"', puml_content)

if __name__ == '__main__':
    unittest.main()