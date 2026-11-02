#include "pointer_operations.h"

#include <stdexcept>

void computeWithPointers(const int* pa, const int* pb, long long* pSum, long long* pDiff) {
    if (!pa || !pb || !pSum || !pDiff) throw std::invalid_argument("Null pointer received.");
    // Widen to long long BEFORE calculating so two 32-bit ints can never overflow.
    long long x = *pa;                   // *pa = dereference: "the value pa points to"
    long long y = *pb;
    *pSum = x + y;
    long long d = x - y;
    *pDiff = (d < 0) ? -d : d;
}

PointerResult runPointerOperations(int a, int b) {
    PointerResult r;
    r.first = a;
    r.second = b;
    computeWithPointers(&a, &b, &r.sum, &r.absoluteDifference);   // & = pass the address
    return r;
}
