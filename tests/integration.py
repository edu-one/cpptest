# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

import os
import unittest
from subprocess import run
from shutil import rmtree


class TestTemplate(unittest.TestCase):

    @classmethod
    def cwd(cls):
        return os.path.dirname(os.path.abspath(__file__))

    def setUp(self):
        pid = os.getpid()
        self.test_name = f"stubname{pid}"
        self.test_version = "2.7.1"
        self.test_dir = os.path.join(TestTemplate.cwd(), "build", "tests", self.test_name)
        self.project_dir = os.path.join(TestTemplate.cwd(), "..")
        # Create the test directory (remove if already exists)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        rmtree(self.test_dir)

    def test_crete_project(self):
        # obtain conan config home
        conan_home_command = ["conan", "config", "home"]
        result = run(conan_home_command, capture_output=True)
        conan_home = result.stdout.decode("utf-8").strip()
        print(f"Conan home: {conan_home}")
        self.assertTrue(os.path.exists(conan_home))
        self.assertTrue(os.path.isdir(conan_home))

        template_path = os.path.join(conan_home, "templates", "command", "new", "dv", "cpptest")
        if os.path.exists(template_path):
            print(f"Removing existing template: {template_path}")
            rmtree(template_path)

        # check that project dir is correctly set
        self.assertTrue(os.path.exists(self.project_dir))
        self.assertTrue(os.path.isdir(self.project_dir))
        # ignored items should not be present in the following list
        expected_fs_items = [
            ".gitignore",
            "LICENSE",
            "README.md",
            "templates",
            "tests",
        ]
        self.check_dir_content(self.project_dir, expected_fs_items)

        # Install the template
        install_template_command = ["conan", "config", "install", "."]
        run(install_template_command, cwd=self.project_dir)
        self.assertTrue(os.path.exists(template_path))
        self.assertTrue(os.path.isdir(template_path))

        # check if the template is installed
        expected_files = [
            "conanfile.py",
            "CMakeLists.txt",
            "include/{{name}}.h",
            "src/{{name}}.cpp",
            ".clang-format",
            ".gitignore",
            ".cmake-format",
            "LICENSE",
            "README.md",
            "requirements.txt",
            "tests/CMakeLists.txt",
            "tests/unit/CMakeLists.txt",
            "tests/unit/{{name}}_test.cpp",
        ]
        self.check_dir_content(template_path, expected_files)

        conan_new_command = ["conan", "new", "dv/cpptest", "-d", f"name={self.test_name}", "-d", f"version={self.test_version}"]
        run(conan_new_command, cwd=self.test_dir)

        # Expected file names
        expected_files = [
            "conanfile.py",
            "CMakeLists.txt",
            f"include/{self.test_name}.h",
            f"src/{self.test_name}.cpp",
            ".clang-format",
            ".gitignore",
            ".cmake-format",
            "LICENSE",
            "README.md",
            "requirements.txt",
            "tests/CMakeLists.txt",
            "tests/unit/CMakeLists.txt",
            f"tests/unit/{self.test_name}_test.cpp",
            ".github/workflows/unit-tests.yml",
            ".vscode/settings.json",
            ".vscode/launch.json",
        ]

        # Check if expected files exist
        self.check_dir_content(self.test_dir, expected_files)

        # Check if the conanfile.py contains the correct name and version
        conanfile_path = os.path.join(self.test_dir, "conanfile.py")
        with open(conanfile_path, "r") as file:
            content = file.read()
            self.assertIn(f'name = \'{self.test_name}\'', content)
            self.assertIn(f'version = \'{self.test_version}\'', content)

        # Check if the CMakeLists.txt contains the correct name, version, file names, etc.
        cmake_path = os.path.join(self.test_dir, "CMakeLists.txt")
        with open(cmake_path, "r") as file:
            content = file.read()
            self.assertIn(f"project({self.test_name} VERSION {self.test_version} LANGUAGES CXX)", content)
            self.assertIn(f"add_library({self.test_name} src/{self.test_name}.cpp)", content)
            self.assertIn(f"target_include_directories({self.test_name} PUBLIC include)", content)
        
        # Check if new project can be built & tested
        build_dir = os.path.join(self.test_dir, "build")
        # configure dependencies of the project
        configure_command = ["conan", "install", ".", "--build=missing", "-s", "build_type=Release"]
        run(configure_command, cwd=self.test_dir)
        # configure the project
        preset_name = "conan-release"
        build_command = ["cmake", "--preset", preset_name]
        run(build_command, cwd=self.test_dir)
        # build the project
        build_command = ["cmake", "--build", "--preset", preset_name]
        run(build_command, cwd=self.test_dir)
        # test the project
        test_command = ["ctest", "--preset", preset_name]
        run(test_command, cwd=self.test_dir)

    def check_dir_content(self, template_path, expected):
        for fs_item in expected:
            path = os.path.join(template_path, fs_item)
            self.assertTrue(os.path.exists(path), f"FS item {fs_item} not found in {template_path}")


if __name__ == "__main__":
    unittest.main()
