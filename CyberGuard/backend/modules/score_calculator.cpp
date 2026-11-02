#include "score_calculator.h"

#include <cstdarg>
#include <stdexcept>

bool safeAdd(long long a, long long b, long long& out) {
    long long result;
    if (__builtin_add_overflow(a, b, &result)) return false;   // GCC/Clang built-in check
    out = result;
    return true;
}

long long sumVariadic(int count, ...) {
    va_list args;
    va_start(args, count);
    long long total = 0;
    for (int i = 0; i < count; ++i) {
        int value = va_arg(args, int);
        if (!safeAdd(total, value, total)) {
            va_end(args);
            throw std::overflow_error("The sum is too large to calculate safely.");
        }
    }
    va_end(args);
    return total;
}

ScoreResult calculateScores(const std::vector<int>& scores) {
    if (scores.empty() || scores.size() > 10)
        throw std::invalid_argument("Enter between 1 and 10 scores.");
    ScoreResult r;
    r.count = static_cast<int>(scores.size());
    r.minimum = r.maximum = scores[0];
    for (int s : scores) {
        if (!safeAdd(r.sum, s, r.sum))
            throw std::overflow_error("The sum is too large to calculate safely.");
        if (s < r.minimum) r.minimum = s;
        if (s > r.maximum) r.maximum = s;
    }
    r.average = static_cast<double>(r.sum) / r.count;
    return r;
}
