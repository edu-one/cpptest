# Copyright (C) Denys Valchuk. Licensed under the MIT License (see LICENSE).
# ZHZhbGNodWtAZ21haWwuY29tCg==

import json
import os
import sys
import unittest
from subprocess import run
from shutil import rmtree


class TestTemplate(unittest.TestCase):

    # cmake --preset selection is generator-dependent: Windows gets a multi-config VS
    # generator, where the *configure* preset is "conan-default" and only the
    # *build*/*test* presets are "conan-release"; Linux's single-config generator uses
    # "conan-release" for all three.
    CONFIGURE_PRESET = "conan-default" if sys.platform == "win32" else "conan-release"
    BUILD_PRESET = "conan-release"

    @classmethod
    def cwd(cls):
        return os.path.dirname(os.path.abspath(__file__))

    @classmethod
    def setUpClass(cls):
        # Point every subprocess at a throwaway Conan home instead of the developer's
        # real ~/.conan2, so this suite never reads or mutates it. Kept under the
        # repo's own build/ tree rather than the OS temp dir: on Windows, a
        # CONAN_HOME under %TEMP% escalates MSBuild's MSB8029 into a failed
        # try-compile, breaking every from-source build at configure time.
        #
        # Scoped to the whole class (not per-test): with --build=missing and no
        # ConanCenter prebuilt matching the detected profile for gtest/1.14.0,
        # wiping this per test forced gtest to compile from source in every one
        # of the tests that run `conan install`/`conan create`, instead of once
        # for the whole suite.
        pid = os.getpid()
        cls.conan_home = os.path.join(cls.cwd(), "build", "conan-home", f"suite{pid}")
        if os.path.exists(cls.conan_home):
            rmtree(cls.conan_home)
        os.makedirs(cls.conan_home)
        cls.env = os.environ.copy()
        cls.env["CONAN_HOME"] = cls.conan_home

        # A freshly isolated Conan home has no default profile yet.
        cls._run_class_setup_command(["conan", "profile", "detect", "--force"])

        # Every test below needs the template installed into the isolated Conan home,
        # so do it once here rather than duplicating it in each test.
        project_dir = os.path.join(cls.cwd(), "..")
        cls._run_class_setup_command(["conan", "config", "install", "."], cwd=project_dir)

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.conan_home)

    @classmethod
    def _run_class_setup_command(cls, command, cwd=None):
        """Like run_checked, but usable from setUpClass/tearDownClass where no
        TestCase instance (and thus no self.assertEqual) exists yet."""
        result = run(command, cwd=cwd, env=cls.env, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(
                "Command {} failed with exit code {}\n--- stdout ---\n{}\n--- stderr ---\n{}".format(
                    command,
                    result.returncode,
                    result.stdout.decode("utf-8", errors="replace"),
                    result.stderr.decode("utf-8", errors="replace"),
                )
            )

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

        # self.conan_home/self.env resolve to the class attributes set in
        # setUpClass (shared Conan package cache for the whole suite run).
        self.template_path = os.path.join(
            self.conan_home, "templates", "command", "new", "dv", "cpptest"
        )

        self.hyphen_name = f"my-lib-{pid}"
        self.hyphen_package_name = self.hyphen_name.replace("-", "_")
        self.hyphen_dir = os.path.join(self.test_dir, "hyphen-case")

    def tearDown(self):
        rmtree(self.test_dir)

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

    def check_dir_content(self, path, expected):
        for fs_item in expected:
            item_path = os.path.join(path, fs_item)
            self.assertTrue(os.path.exists(item_path), f"FS item {fs_item} not found in {path}")

    # ---- shared helpers for the generate/configure/build/ctest/create sequence ----

    def generate_project(self, name, version, target_dir):
        """Run `conan new dv/cpptest` for the given name/version into target_dir."""
        os.makedirs(target_dir, exist_ok=True)
        conan_new_command = [
            "conan", "new", "dv/cpptest", "-d", f"name={name}", "-d", f"version={version}",
        ]
        self.run_checked(conan_new_command, cwd=target_dir)

    def build_and_test_project(self, project_dir):
        """Configure, build, and ctest a generated project, using the generator-aware
        configure preset (see CONFIGURE_PRESET)."""
        configure_command = ["conan", "install", ".", "--build=missing", "-s", "build_type=Release"]
        self.run_checked(configure_command, cwd=project_dir)
        self.run_checked(["cmake", "--preset", self.CONFIGURE_PRESET], cwd=project_dir)
        self.run_checked(["cmake", "--build", "--preset", self.BUILD_PRESET], cwd=project_dir)
        self.run_checked(["ctest", "--preset", self.BUILD_PRESET], cwd=project_dir)

    def create_package(self, name, project_dir):
        """Run `conan create` for the given package name and return its package_folder."""
        create_command = [
            "conan", "create", ".", "--build=missing", "-s", "build_type=Release", "--format=json",
        ]
        create_result = self.run_checked(create_command, cwd=project_dir)
        create_info = json.loads(create_result.stdout)
        package_node = next(
            node for node in create_info["graph"]["nodes"].values()
            if node.get("name") == name
        )
        return package_node["package_folder"]

    def assert_package_nonempty(self, package_folder, name):
        """Regression check for a confirmed defect: `conan create` used to exit 0 while
        producing an EMPTY package (missing install() rules in CMakeLists.txt meant
        cmake.install() copied nothing, even though package_info() advertised a
        library). Assert the package actually contains the library and the installed
        header, not just conaninfo.txt / conanmanifest.txt."""
        self.assertTrue(
            os.path.isdir(package_folder), f"Package folder does not exist: {package_folder}"
        )

        header_path = os.path.join(package_folder, "include", f"{name}.h")
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

    # ---- tests ----

    def test_template_installation(self):
        """`conan config home` resolves inside the isolated home, the repo's own
        top-level layout is intact, and the template was installed there with all
        expected files."""
        conan_home_command = ["conan", "config", "home"]
        result = self.run_checked(conan_home_command)
        conan_home = result.stdout.decode("utf-8").strip()
        self.assertTrue(os.path.exists(conan_home))
        self.assertTrue(os.path.isdir(conan_home))

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

        self.assertTrue(os.path.exists(self.template_path))
        self.assertTrue(os.path.isdir(self.template_path))

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
        self.check_dir_content(self.template_path, expected_files)

    def test_default_name_generation(self):
        """Generating a project with a plain (non-hyphenated) name produces the
        expected file set, and conanfile.py / CMakeLists.txt / header content are
        correctly interpolated."""
        self.generate_project(self.test_name, self.test_version, self.test_dir)

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

    def test_default_name_build_and_test(self):
        """A generated default-name project configures, builds, and passes ctest
        end-to-end (using the generator-aware configure preset)."""
        self.generate_project(self.test_name, self.test_version, self.test_dir)
        self.build_and_test_project(self.test_dir)

    def test_default_name_conan_create(self):
        """`conan create` packages a default-name project with a non-empty package."""
        self.generate_project(self.test_name, self.test_version, self.test_dir)
        package_folder = self.create_package(self.test_name, self.test_dir)
        self.assert_package_nonempty(package_folder, self.test_name)

    def test_hyphenated_name_generation(self):
        """Regression test for a confirmed defect (S4): a hyphenated Conan package
        name like "my-lib" used to be interpolated verbatim into C++/Python
        identifier positions (include guard, namespace, conanfile.py class name),
        producing invalid C++ syntax and a Python SyntaxError. The template now
        uses Conan's injected {{package_name}} Jinja variable in those spots,
        which sanitizes '-'/'.'/'+' to '_' (as_package_name), while {{name}}
        (still hyphenated) stays in file names and the actual Conan package name."""
        self.generate_project(self.hyphen_name, self.test_version, self.hyphen_dir)

        # File names and the Conan package name itself stay hyphenated ({{name}}).
        hyphen_header_src_path = os.path.join(self.hyphen_dir, "include", f"{self.hyphen_name}.h")
        self.assertTrue(os.path.exists(hyphen_header_src_path), f"Header not found: {hyphen_header_src_path}")

        # But the include guard and namespace must be sanitized, valid C++ identifiers.
        with open(hyphen_header_src_path, "r") as file:
            hyphen_header_content = file.read()
        self.assertIn(f"DV_{self.hyphen_package_name.upper()}_H_", hyphen_header_content)
        self.assertIn(f"namespace dv::{self.hyphen_package_name} {{", hyphen_header_content)
        self.assertIn(f"}} // namespace dv::{self.hyphen_package_name}", hyphen_header_content)
        self.assertNotIn("-", hyphen_header_content.split("*/", 1)[1])

        # The conanfile.py class name must be a valid Python identifier too, while
        # the actual `name =` field stays hyphenated (it's the Conan package name).
        hyphen_conanfile_path = os.path.join(self.hyphen_dir, "conanfile.py")
        with open(hyphen_conanfile_path, "r") as file:
            hyphen_conanfile_content = file.read()
        self.assertIn(
            f"class {self.hyphen_package_name.capitalize()}Conan(ConanFile):", hyphen_conanfile_content
        )
        self.assertIn(f"name = '{self.hyphen_name}'", hyphen_conanfile_content)
        # Would raise SyntaxError before S4's fix -- prove it's now valid Python.
        compile(hyphen_conanfile_content, hyphen_conanfile_path, "exec")

    def test_hyphenated_name_build_and_test(self):
        """Build it end-to-end: configure + build + ctest, where it previously
        would have failed to even parse (before S4's sanitization fix)."""
        self.generate_project(self.hyphen_name, self.test_version, self.hyphen_dir)
        self.build_and_test_project(self.hyphen_dir)

    def test_hyphenated_name_conan_create(self):
        """`conan create`, mirroring the default-name non-empty-package check."""
        self.generate_project(self.hyphen_name, self.test_version, self.hyphen_dir)
        package_folder = self.create_package(self.hyphen_name, self.hyphen_dir)
        self.assert_package_nonempty(package_folder, self.hyphen_name)


if __name__ == "__main__":
    unittest.main()
