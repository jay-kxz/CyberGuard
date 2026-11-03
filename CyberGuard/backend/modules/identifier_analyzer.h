// Module 1: Identifier Analyzer (arrays, strings, loops, functions)
#ifndef IDENTIFIER_ANALYZER_H
#define IDENTIFIER_ANALYZER_H
#include <array>
#include <string>
#include <vector>

struct IdentifierResult {
    std::array<int, 10> digitFrequency{};  // index = the digit (0..9)
    int totalDigits = 0;
    int totalLetters = 0;
    int totalOthers = 0;                   // spaces, symbols and non-ASCII bytes
    int maxFrequency = 0;
    std::vector<int> mostFrequentDigits;   // every digit that reaches maxFrequency
};

IdentifierResult analyzeIdentifier(const std::string& text);
#endif
