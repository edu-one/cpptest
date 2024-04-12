/* Copyright (C) Denys Valchuk - All Rights Reserved
 * ZHZhbGNodWtAZ21haWwuY29tCg==
 */

#include "{{name}}.h"

#include <stdexcept>

int dv::{{name}}::factorial(int n) {
    if (n < 0)
        throw std::invalid_argument("Factorial of negative number is undefined");
    if (n == 0)
        return 1;
    return n * factorial(n - 1);
}
