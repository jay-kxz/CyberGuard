// Simple C++ tests for modules 1-4. Build and run with tests/cpp_tests/run_tests.bat
#include <climits>
#include <iostream>
#include <stdexcept>
#include "modules/identifier_analyzer.h"
#include "modules/pointer_operations.h"
#include "modules/score_calculator.h"
#include "modules/user_assessment.h"

static int passed = 0, failed = 0;
#define CHECK(cond) do { if (cond) { ++passed; } else { ++failed; \
    std::cout << "FAIL line " << __LINE__ << ": " #cond "\n"; } } while (0)

template <typename F> bool throwsInvalid(F f) {
    try { f(); } catch (const std::invalid_argument&) { return true; } catch (...) {}
    return false;
}

int main() {
    // Identifier Analyzer
    auto id = analyzeIdentifier("AB12 3C 4@4 99");
    CHECK(id.totalDigits == 7 && id.totalLetters == 3 && id.totalOthers == 4);
    CHECK(id.digitFrequency[4] == 2 && id.digitFrequency[9] == 2 && id.digitFrequency[0] == 0);
    CHECK(id.maxFrequency == 2 && id.mostFrequentDigits == std::vector<int>({4, 9}));
    auto none = analyzeIdentifier("abc");
    CHECK(none.maxFrequency == 0 && none.mostFrequentDigits.empty());

    // Score Calculator
    auto sc = calculateScores({72, 85, 90});
    CHECK(sc.count == 3 && sc.sum == 247 && sc.minimum == 72 && sc.maximum == 90);
    CHECK(sc.average > 82.33 && sc.average < 82.34);
    CHECK(throwsInvalid([] { calculateScores({}); }));
    CHECK(throwsInvalid([] { calculateScores(std::vector<int>(11, 1)); }));
    long long out = 5;
    CHECK(!safeAdd(LLONG_MAX, 1, out) && out == 5);
    CHECK(safeAdd(2, 3, out) && out == 5);
    CHECK(sumVariadic(3, 10, 20, 30) == 60 && sumVariadic(0) == 0);
    CHECK(calculateScores({INT_MAX, INT_MAX}).sum == 4294967294LL);

    // Pointer Operations
    auto p = runPointerOperations(7, -3);
    CHECK(p.sum == 4 && p.absoluteDifference == 10);
    auto big = runPointerOperations(INT_MAX, INT_MIN);
    CHECK(big.sum == -1 && big.absoluteDifference == 4294967295LL);
    CHECK(throwsInvalid([] { computeWithPointers(nullptr, nullptr, nullptr, nullptr); }));

    // User Assessment
    CHECK(throwsInvalid([] { UserAssessment("Asha", {1, 2, 3, 4, 101}); }));
    CHECK(throwsInvalid([] { UserAssessment("Asha", {1, 2, 3}); }));
    CHECK(throwsInvalid([] { UserAssessment("", {1, 2, 3, 4, 5}); }));
    AssessmentBoard board;
    UserAssessment asha("Asha", {60, 70, 80, 90, 75});
    CHECK(asha.total() == 375 && asha.average() == 75.0 && asha.result(50) == "PASS");
    board.add(asha);
    board.add(UserAssessment("Ravi", {10, 20, 30, 40, 50}));
    auto s = board.summarize(50);
    CHECK(s.users == 2 && s.atOrAboveBaseline == 1);
    CHECK(s.highestUser == "Asha" && s.lowestUser == "Ravi" && s.lowestAverage == 30.0);
    board.add(UserAssessment("Asha", {0, 0, 0, 0, 0}));   // same name replaces
    CHECK(board.size() == 2);

    std::cout << passed << " checks passed, " << failed << " failed\n";
    return failed == 0 ? 0 : 1;
}
