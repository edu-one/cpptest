# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

cmake_minimum_required(VERSION 3.23)

project({{name}} VERSION {{version|default("0.0.1", true)}} LANGUAGES CXX)

set(CMAKE_CXX_EXTENSIONS OFF)

include(GNUInstallDirs)

option(WITH_TESTS "build tests?" ON)

add_library({{name}} src/{{name}}.cpp)
target_include_directories({{name}} PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>)
target_compile_features({{name}} PUBLIC cxx_std_20)

install(TARGETS {{name}}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES include/{{name}}.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if(WITH_TESTS AND PROJECT_IS_TOP_LEVEL)
  list(APPEND CMAKE_CTEST_ARGUMENTS "--output-on-failure")
  enable_testing()
  add_subdirectory(tests)
endif()
