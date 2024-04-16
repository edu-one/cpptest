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
        # Create the test directory (remove if already exists)
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        rmtree(self.test_dir)

    def test_crete_project(self):
        command = ["conan", "new", "dv_cpptest", "-d", f"name={self.test_name}", "-d", f"version={self.test_version}"]
        # Run the command in the test directory
        run(command, cwd=self.test_dir)

        # Expected file names
        expected_files = [
            "conanfile.py",
            "CMakeLists.txt",
            f"include/{self.test_name}.h",
            f"src/{self.test_name}.cpp",
            ".clang-format",
            ".gitignore",
            ".cmake-format",
            ".conanignore",
            "LICENSE",
            "README.md",
            "requirements.txt",
            "tests/CMakeLists.txt",
            "tests/unit/CMakeLists.txt",
            f"tests/unit/{self.test_name}_test.cpp",
        ]

        # Check if expected files exist
        for filename in expected_files:
            filepath = os.path.join(self.test_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"File {filename} not found")

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
        configure_command = ["conan", "install", ".", "--build=missing"]
        run(configure_command, cwd=self.test_dir)
        # configure the project
        preset_name = "conan-debug"
        build_command = ["cmake", "--preset", preset_name]
        run(build_command, cwd=self.test_dir)
        # build the project
        build_command = ["cmake", "--build", "--preset", preset_name]
        run(build_command, cwd=self.test_dir)
        # test the project
        test_command = ["ctest", "--preset", preset_name]
        run(test_command, cwd=self.test_dir)


if __name__ == "__main__":
    unittest.main()
