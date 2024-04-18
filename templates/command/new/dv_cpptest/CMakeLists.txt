# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

cmake_minimum_required(VERSION 3.23)

project({{name}} VERSION {{version}} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

option(WITH_TESTS "build tests?" ON)

add_library({{name}} src/{{name}}.cpp)
target_include_directories({{name}} PUBLIC include)

if(WITH_TESTS)
  list(APPEND CMAKE_CTEST_ARGUMENTS "--output-on-failure")
  enable_testing()
  add_subdirectory(tests)
endif()
