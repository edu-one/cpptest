# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

include(CMakePrintHelpers)

add_executable({{name}}_test {{name}}_test.cpp)

find_package(GTest)
target_link_libraries({{name}}_test 
        PRIVATE {{name}}
        gtest::gtest)

include(GoogleTest)
gtest_discover_tests({{name}}_test)
