/* Copyright (C) Denys Valchuk - All Rights Reserved
 * ZHZhbGNodWtAZ21haWwuY29tCg==
 */

#include <some.h>
#include <gtest/gtest.h>

TEST(FactorialTest, Zero) {
  EXPECT_EQ(1, dv::some::factorial(0));
}

TEST(FactorialTest, Positive) {
  EXPECT_EQ(1, dv::some::factorial(1));
  EXPECT_EQ(2, dv::some::factorial(2));
  EXPECT_EQ(6, dv::some::factorial(3));
  EXPECT_EQ(40320, dv::some::factorial(8));
}

TEST(FactorialTest, Negative) {
  EXPECT_THROW(dv::some::factorial(-1), std::invalid_argument);
}
