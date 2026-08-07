# Copyright (C) Denys Valchuk. Licensed under the MIT License (see LICENSE).
# ZHZhbGNodWtAZ21haWwuY29tCg==

import json
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
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)
        os.makedirs(self.test_dir)

        # Point every subprocess at a throwaway Conan home instead of the developer's
        # real ~/.conan2, so this test never reads or mutates it. Kept under the repo's
        # own build/ tree rather than the OS temp dir: on Windows, a CONAN_HOME under
        # %TEMP% escalates MSBuild's MSB8029 into a failed try-compile, breaking every
        # from-source build at configure time.
        self.conan_home = os.path.join(TestTemplate.cwd(), "build", "conan-home", self.test_name)
        if os.path.exists(self.conan_home):
            rmtree(self.conan_home)
        os.makedirs(self.conan_home)
        self.env = os.environ.copy()
        self.env["CONAN_HOME"] = self.conan_home

        # A freshly isolated Conan home has no default profile yet.
        self.run_checked(["conan", "profile", "detect", "--force"])

    def tearDown(self):
        rmtree(self.test_dir)
        rmtree(self.conan_home)

    def run_checked(self, command, cwd=None):
        """Run a subprocess against the isolated Conan home and fail the test - with
        the captured stdout/stderr in the failure message - if it exits non-zero."""
        result = run(command, cwd=cwd, env=self.env, capture_output=True)
        self.assertEqual(
            result.returncode,
            0,
            "Command {} failed with exit code {}\n--- stdout ---\n{}\n--- stderr ---\n{}".format(
                command,
                result.returncode,
                result.stdout.decode("utf-8", errors="replace"),
                result.stderr.decode("utf-8", errors="replace"),
            ),
        )
        return result

    def test_create_project(self):
        # obtain conan config home
        conan_home_command = ["conan", "config", "home"]
        result = self.run_checked(conan_home_command)
        conan_home = result.stdout.decode("utf-8").strip()
        print(f"Conan home: {conan_home}")
        self.assertTrue(os.path.exists(conan_home))
        self.assertTrue(os.path.isdir(conan_home))

        template_path = os.path.join(conan_home, "templates", "command", "new", "dv", "cpptest")

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
        self.run_checked(install_template_command, cwd=self.project_dir)
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
        self.run_checked(conan_new_command, cwd=self.test_dir)

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
            self.assertIn(f"target_include_directories({self.test_name} PUBLIC", content)
            self.assertIn("$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>", content)
            self.assertIn("$<INSTALL_INTERFACE:include>", content)
            self.assertIn(f"install(TARGETS {self.test_name}", content)

        # Check that the generated header uses dv::<name> for the include guard and
        # namespace. The default test name has no '-', '.', or '+', so {{name}} and
        # {{package_name}} (S4's sanitized identifier variable) render identically
        # here -- confirming S4 didn't change this, unhyphenated, flow.
        header_path = os.path.join(self.test_dir, "include", f"{self.test_name}.h")
        with open(header_path, "r") as file:
            content = file.read()
            self.assertIn(f"DV_{self.test_name.upper()}_H_", content)
            self.assertIn(f"namespace dv::{self.test_name} {{", content)

        # Check if new project can be built & tested
        build_dir = os.path.join(self.test_dir, "build")
        # configure dependencies of the project
        configure_command = ["conan", "install", ".", "--build=missing", "-s", "build_type=Release"]
        self.run_checked(configure_command, cwd=self.test_dir)
        # configure the project
        preset_name = "conan-release"
        build_command = ["cmake", "--preset", preset_name]
        self.run_checked(build_command, cwd=self.test_dir)
        # build the project
        build_command = ["cmake", "--build", "--preset", preset_name]
        self.run_checked(build_command, cwd=self.test_dir)
        # test the project
        test_command = ["ctest", "--preset", preset_name]
        self.run_checked(test_command, cwd=self.test_dir)

        # Regression test for a confirmed defect: `conan create` used to exit 0 while
        # producing an EMPTY package (missing install() rules in CMakeLists.txt meant
        # cmake.install() copied nothing, even though package_info() advertised a
        # library). Run the real packaging flow and assert the package actually
        # contains the library and the installed header, not just conaninfo.txt /
        # conanmanifest.txt.
        create_command = [
            "conan", "create", ".", "--build=missing", "-s", "build_type=Release", "--format=json",
        ]
        create_result = self.run_checked(create_command, cwd=self.test_dir)
        create_info = json.loads(create_result.stdout)
        package_node = next(
            node for node in create_info["graph"]["nodes"].values()
            if node.get("name") == self.test_name
        )
        package_folder = package_node["package_folder"]
        self.assertTrue(
            os.path.isdir(package_folder), f"Package folder does not exist: {package_folder}"
        )

        header_path = os.path.join(package_folder, "include", f"{self.test_name}.h")
        self.assertTrue(os.path.exists(header_path), f"Installed header not found: {header_path}")

        lib_dir = os.path.join(package_folder, "lib")
        self.assertTrue(os.path.isdir(lib_dir), f"lib/ directory not found in package: {package_folder}")
        self.assertTrue(os.listdir(lib_dir), f"No library file found in {lib_dir}")

        metadata_only_files = {"conaninfo.txt", "conanmanifest.txt"}
        package_files = set(os.listdir(package_folder))
        self.assertFalse(
            package_files <= metadata_only_files,
            f"Package folder contains only metadata files, no lib/headers: {package_files}",
        )

        # Regression test for a confirmed defect (S4): a hyphenated Conan package
        # name like "my-lib" used to be interpolated verbatim into C++/Python
        # identifier positions (include guard, namespace, conanfile.py class name),
        # producing invalid C++ syntax and a Python SyntaxError. The template now
        # uses Conan's injected {{package_name}} Jinja variable in those spots,
        # which sanitizes '-'/'.'/'+' to '_' (as_package_name), while {{name}}
        # (still hyphenated) stays in file names and the actual Conan package name.
        # Reuses this test's already-installed template and isolated Conan home;
        # generated into its own subdirectory so it doesn't collide with the
        # default-name project above.
        hyphen_name = f"my-lib-{os.getpid()}"
        hyphen_package_name = hyphen_name.replace("-", "_")
        hyphen_dir = os.path.join(self.test_dir, "hyphen-case")
        os.makedirs(hyphen_dir)

        conan_new_hyphen_command = [
            "conan", "new", "dv/cpptest", "-d", f"name={hyphen_name}", "-d", f"version={self.test_version}",
        ]
        self.run_checked(conan_new_hyphen_command, cwd=hyphen_dir)

        # File names and the Conan package name itself stay hyphenated ({{name}}).
        hyphen_header_src_path = os.path.join(hyphen_dir, "include", f"{hyphen_name}.h")
        self.assertTrue(os.path.exists(hyphen_header_src_path), f"Header not found: {hyphen_header_src_path}")

        # But the include guard and namespace must be sanitized, valid C++ identifiers.
        with open(hyphen_header_src_path, "r") as file:
            hyphen_header_content = file.read()
        self.assertIn(f"DV_{hyphen_package_name.upper()}_H_", hyphen_header_content)
        self.assertIn(f"namespace dv::{hyphen_package_name} {{", hyphen_header_content)
        self.assertIn(f"}} // namespace dv::{hyphen_package_name}", hyphen_header_content)
        self.assertNotIn("-", hyphen_header_content.split("*/", 1)[1])

        # The conanfile.py class name must be a valid Python identifier too, while
        # the actual `name =` field stays hyphenated (it's the Conan package name).
        hyphen_conanfile_path = os.path.join(hyphen_dir, "conanfile.py")
        with open(hyphen_conanfile_path, "r") as file:
            hyphen_conanfile_content = file.read()
        self.assertIn(f"class {hyphen_package_name.capitalize()}Conan(ConanFile):", hyphen_conanfile_content)
        self.assertIn(f"name = '{hyphen_name}'", hyphen_conanfile_content)
        # Would raise SyntaxError before S4's fix -- prove it's now valid Python.
        compile(hyphen_conanfile_content, hyphen_conanfile_path, "exec")

        # Build it end-to-end: configure + build + ctest, where it previously
        # would have failed to even parse.
        configure_command = ["conan", "install", ".", "--build=missing", "-s", "build_type=Release"]
        self.run_checked(configure_command, cwd=hyphen_dir)
        build_command = ["cmake", "--preset", preset_name]
        self.run_checked(build_command, cwd=hyphen_dir)
        build_command = ["cmake", "--build", "--preset", preset_name]
        self.run_checked(build_command, cwd=hyphen_dir)
        test_command = ["ctest", "--preset", preset_name]
        self.run_checked(test_command, cwd=hyphen_dir)

        # And conan create, mirroring the non-empty-package check above.
        create_command = [
            "conan", "create", ".", "--build=missing", "-s", "build_type=Release", "--format=json",
        ]
        hyphen_create_result = self.run_checked(create_command, cwd=hyphen_dir)
        hyphen_create_info = json.loads(hyphen_create_result.stdout)
        hyphen_package_node = next(
            node for node in hyphen_create_info["graph"]["nodes"].values()
            if node.get("name") == hyphen_name
        )
        hyphen_package_folder = hyphen_package_node["package_folder"]
        self.assertTrue(os.path.isdir(hyphen_package_folder))
        hyphen_header_pkg_path = os.path.join(hyphen_package_folder, "include", f"{hyphen_name}.h")
        self.assertTrue(os.path.exists(hyphen_header_pkg_path))
        hyphen_lib_dir = os.path.join(hyphen_package_folder, "lib")
        self.assertTrue(os.path.isdir(hyphen_lib_dir))
        self.assertTrue(os.listdir(hyphen_lib_dir))

    def check_dir_content(self, template_path, expected):
        for fs_item in expected:
            path = os.path.join(template_path, fs_item)
            self.assertTrue(os.path.exists(path), f"FS item {fs_item} not found in {template_path}")


if __name__ == "__main__":
    unittest.main()
