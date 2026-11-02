// Module 3: Pointer Operations (pass by address, dereferencing)
#ifndef POINTER_OPERATIONS_H
#define POINTER_OPERATIONS_H

struct PointerResult {
    int first = 0;
    int second = 0;
    long long sum = 0;
    long long absoluteDifference = 0;
};

// Reads *pa and *pb, writes the answers through pSum and pDiff. Throws if any pointer is null.
void computeWithPointers(const int* pa, const int* pb, long long* pSum, long long* pDiff);

PointerResult runPointerOperations(int a, int b);
#endif
