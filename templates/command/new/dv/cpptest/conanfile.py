# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout

required_conan_version = ">=2.2"

class {{name|capitalize}}Conan(ConanFile):
    name = '{{name}}'
    version = '{{version|default("0.0.1", true)}}'
    license = "{{license|default("MIT", true)}}"

    author = "Denys Valchuk <ZHZhbGNodWtAZ21haWwuY29tCg==>"
    url = "https://github.com/valden/{{name}}"
    description = "C++ test package with tests"
    topics = ("{{name}}", "algo", "playground")

    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_tests": [True, False]
               }
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_tests": True
                       }

    exports_sources = "CMakeLists.txt", "cmake/*", "include/*", "src/*", \
                      "tests/**"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.compiler.cppstd = 20
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["WITH_TESTS"] = bool(self.options.with_tests)
        tc.generate()

    def requirements(self):
        if self.options.with_tests:
            self.test_requires("gtest/1.17.0")

    def package_id(self):
        del self.info.options.with_tests

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        # project is small - so it is not an issue to run tests each build
        if self.options.with_tests:
            cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["{{name}}"]
