// Simple C++ tests for modules 1-4. Build and run with tests/cpp_tests/run_tests.bat
#include <climits>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include "modules/file_integrity.h"
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

template <typename F> bool throwsRuntime(F f) {
    try { f(); } catch (const std::runtime_error&) { return true; } catch (...) {}
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

    // File Integrity (Module 5): the four published SHA-256 test vectors.
    CHECK(sha256Hex("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");
    CHECK(sha256Hex("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad");
    CHECK(sha256Hex("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq") ==
          "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1");
    CHECK(sha256Hex(std::string(1000000, 'a')) ==
          "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0");
    CHECK(isSha256Hex(std::string(64, '0')) && !isSha256Hex("xyz") && !isSha256Hex(std::string(63, 'a')));
    CHECK(verifyHash(sha256Hex("abc"), "") == "NO REFERENCE GIVEN");
    CHECK(verifyHash(sha256Hex("abc"),
                     "BA7816BF8F01CFEA414140DE5DAE2223B00361A396177A9CB410FF61F20015AD") == "MATCH");
    CHECK(verifyHash(sha256Hex("abc"), std::string(64, 'f')) == "MISMATCH");
    CHECK(throwsInvalid([] { verifyHash(sha256Hex("abc"), "not-a-hash"); }));

    // The same hash, read from a real file in 64 KB blocks (file handling).
    const auto path = (std::filesystem::temp_directory_path() / "cyberguard_test_file.tmp").string();
    {
        std::ofstream out(path, std::ios::binary);
        out << "abc";
    }
    auto hashed = sha256File(path);
    CHECK(hashed.sha256 == sha256Hex("abc") && hashed.bytes == 3);
    std::remove(path.c_str());
    CHECK(throwsRuntime([] { sha256File("this_file_does_not_exist_12345.tmp"); }));

    std::cout << passed << " checks passed, " << failed << " failed\n";
    return failed == 0 ? 0 : 1;
}
