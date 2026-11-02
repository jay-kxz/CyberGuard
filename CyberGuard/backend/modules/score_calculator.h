// Module 2: Score Calculator (variadic function, overflow-safe arithmetic)
#ifndef SCORE_CALCULATOR_H
#define SCORE_CALCULATOR_H
#include <vector>

struct ScoreResult {
    int count = 0;
    long long sum = 0;
    int minimum = 0;
    int maximum = 0;
    double average = 0.0;
};

// Adds a + b into out. Returns false (and leaves out unchanged) if it would overflow.
bool safeAdd(long long a, long long b, long long& out);

// Variadic function: sumVariadic(3, 10, 20, 30) == 60. Every extra argument must be an int.
long long sumVariadic(int count, ...);

// Accepts 1 to 10 scores. Throws std::invalid_argument or std::overflow_error.
ScoreResult calculateScores(const std::vector<int>& scores);
#endif
