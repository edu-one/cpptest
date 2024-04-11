# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout

class {{name|capitalize}}Conan(ConanFile):
    minimum_conan_version = '2.2'
    name = '{{name}}'
    version = '{{version}}'
    license = "{{license|default("MIT", true)}}"

    author = "Denys Valchuk <ZHZhbGNodWtAZ21haWwuY29tCg==>"
    url = "https://github.com/valden/conan-some"
    description = "C++ test package with tests"
    topics = ("{{name}}", "algo", "playground")

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

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["WITH_TESTS"] = bool(self.options.with_tests)
        tc.variables["CMAKE_BUILD_TYPE"] = "%s" % self.settings.build_type
        tc.generate()

    def requirements(self):
        if self.options.with_tests:
            self.requires("gtest/1.14.0")

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
