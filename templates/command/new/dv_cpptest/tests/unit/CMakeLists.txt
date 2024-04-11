# Copyright (C) Denys Valchuk - All Rights Reserved
# ZHZhbGNodWtAZ21haWwuY29tCg==

include(CMakePrintHelpers)

add_executable(factorial_test factorial_test.cpp)

find_package(GTest)
target_link_libraries(factorial_test 
        PRIVATE some
        gtest::gtest)

include(GoogleTest)
gtest_discover_tests(factorial_test)
