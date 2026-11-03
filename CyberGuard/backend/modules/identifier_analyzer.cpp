#include "identifier_analyzer.h"

IdentifierResult analyzeIdentifier(const std::string& text) {
    IdentifierResult r;
    for (unsigned char ch : text) {          // unsigned avoids negative values for non-ASCII bytes
        if (ch >= '0' && ch <= '9') {
            r.digitFrequency[ch - '0']++;
            r.totalDigits++;
        } else if ((ch >= 'A' && ch <= 'Z') || (ch >= 'a' && ch <= 'z')) {
            r.totalLetters++;
        } else {
            r.totalOthers++;
        }
    }
    for (int count : r.digitFrequency)
        if (count > r.maxFrequency) r.maxFrequency = count;
    if (r.maxFrequency > 0)
        for (int d = 0; d < 10; ++d)
            if (r.digitFrequency[d] == r.maxFrequency) r.mostFrequentDigits.push_back(d);
    return r;
}
