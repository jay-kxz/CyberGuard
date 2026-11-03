// Module 5: File Integrity Lab (SHA-256, file handling, byte arrays)
#ifndef FILE_INTEGRITY_H
#define FILE_INTEGRITY_H
#include <string>

struct FileHashResult {
    std::string sha256;                  // always 64 lowercase hexadecimal characters
    unsigned long long bytes = 0;        // how many bytes were read
};

// SHA-256 of a memory buffer. Implemented here so the project needs no extra
// library (no OpenSSL download, no -lcrypto flag on the build line).
std::string sha256Hex(const std::string& data);

// SHA-256 of a file on disk. The file is read in 64 KB blocks, so a large file
// never has to fit in memory. Throws std::runtime_error if it cannot be read.
FileHashResult sha256File(const std::string& path);

// True when text is exactly 64 hexadecimal characters (upper or lower case).
bool isSha256Hex(const std::string& text);

// Compares the calculated hash with a reference hash typed by the user.
// Returns "MATCH", "MISMATCH" or "NO REFERENCE GIVEN" (the same three words the
// database column ck_files_status allows). Throws std::invalid_argument when a
// reference is given but is not 64 hexadecimal characters.
std::string verifyHash(const std::string& actual, const std::string& reference);

#endif
