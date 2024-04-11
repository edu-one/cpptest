# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

cmake_minimum_required(VERSION 3.25)
project(some)

set(CMAKE_CXX_STANDARD 20)

option(WITH_TESTS "build tests?" ON)

add_library(some src/some.cpp)
target_include_directories(some PUBLIC include)

if(WITH_TESTS)
  list(APPEND CMAKE_CTEST_ARGUMENTS "--output-on-failure")
  enable_testing()
  add_subdirectory(tests)
endif()
