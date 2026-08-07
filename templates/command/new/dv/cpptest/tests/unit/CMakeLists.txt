# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

add_executable({{name}}_test {{name}}_test.cpp)

find_package(GTest REQUIRED)
target_link_libraries({{name}}_test 
        PRIVATE {{name}}
        gtest::gtest)

include(GoogleTest)
gtest_discover_tests({{name}}_test)
