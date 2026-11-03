#include "file_integrity.h"

#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <stdexcept>

namespace {

// The 64 round constants from FIPS 180-4. Each is the first 32 bits of the
// fractional part of the cube root of the first 64 prime numbers.
constexpr std::array<std::uint32_t, 64> kRoundConstants = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u, 0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u, 0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu, 0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u, 0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u, 0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u, 0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u, 0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u, 0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u};

// Rotate right: >> would lose the bits that wrap around to the top.
inline std::uint32_t rotateRight(std::uint32_t value, int bits) {
    return (value >> bits) | (value << (32 - bits));
}

inline bool isHexDigit(unsigned char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

// A small streaming SHA-256. Data is added with update() as it arrives, so the
// whole input never has to be stored: the same class hashes memory and files.
class Sha256 {
public:
    Sha256()
        : state_{0x6a09e667u, 0xbb67ae85u, 0x3c6ef372u, 0xa54ff53au,
                 0x510e527fu, 0x9b05688cu, 0x1f83d9abu, 0x5be0cd19u} {}

    void update(const unsigned char* data, std::size_t length) {
        totalBits_ += static_cast<std::uint64_t>(length) * 8u;
        while (length > 0) {
            const std::size_t room = kBlockSize - buffered_;
            const std::size_t take = std::min(length, room);
            std::memcpy(block_.data() + buffered_, data, take);
            buffered_ += take;
            data += take;
            length -= take;
            if (buffered_ == kBlockSize) {
                transform(block_.data());
                buffered_ = 0;
            }
        }
    }

    // Finishes the padding and returns the hash as 64 lowercase hex characters.
    std::string hex() {
        const std::uint64_t bits = totalBits_;          // capture before the padding is added
        const unsigned char marker = 0x80;              // the mandatory single 1 bit
        update(&marker, 1);
        const unsigned char zero = 0x00;
        while (buffered_ != kBlockSize - 8) update(&zero, 1);   // pad until 56 bytes remain

        unsigned char lengthBytes[8];
        for (int i = 0; i < 8; ++i)
            lengthBytes[i] = static_cast<unsigned char>((bits >> (56 - 8 * i)) & 0xFFu);   // big-endian
        update(lengthBytes, 8);

        static const char* digits = "0123456789abcdef";
        std::string out;
        out.reserve(64);
        for (std::uint32_t word : state_)
            for (int shift = 28; shift >= 0; shift -= 4)
                out.push_back(digits[(word >> shift) & 0xFu]);
        return out;
    }

private:
    static constexpr std::size_t kBlockSize = 64;

    void transform(const unsigned char* block) {
        std::uint32_t w[64];
        for (int i = 0; i < 16; ++i) {
            w[i] = (static_cast<std::uint32_t>(block[i * 4]) << 24) |
                   (static_cast<std::uint32_t>(block[i * 4 + 1]) << 16) |
                   (static_cast<std::uint32_t>(block[i * 4 + 2]) << 8) |
                   static_cast<std::uint32_t>(block[i * 4 + 3]);
        }
        for (int i = 16; i < 64; ++i) {
            const std::uint32_t s0 = rotateRight(w[i - 15], 7) ^ rotateRight(w[i - 15], 18) ^ (w[i - 15] >> 3);
            const std::uint32_t s1 = rotateRight(w[i - 2], 17) ^ rotateRight(w[i - 2], 19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16] + s0 + w[i - 7] + s1;
        }

        std::uint32_t a = state_[0], b = state_[1], c = state_[2], d = state_[3];
        std::uint32_t e = state_[4], f = state_[5], g = state_[6], h = state_[7];

        for (int i = 0; i < 64; ++i) {
            const std::uint32_t s1 = rotateRight(e, 6) ^ rotateRight(e, 11) ^ rotateRight(e, 25);
            const std::uint32_t choice = (e & f) ^ (~e & g);
            const std::uint32_t temp1 = h + s1 + choice + kRoundConstants[i] + w[i];
            const std::uint32_t s0 = rotateRight(a, 2) ^ rotateRight(a, 13) ^ rotateRight(a, 22);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temp2 = s0 + majority;
            h = g; g = f; f = e; e = d + temp1;
            d = c; c = b; b = a; a = temp1 + temp2;
        }

        state_[0] += a; state_[1] += b; state_[2] += c; state_[3] += d;
        state_[4] += e; state_[5] += f; state_[6] += g; state_[7] += h;
    }

    std::array<std::uint32_t, 8> state_;
    std::array<unsigned char, kBlockSize> block_{};
    std::size_t buffered_ = 0;
    std::uint64_t totalBits_ = 0;
};

std::string trimmed(const std::string& text) {
    std::size_t first = 0, last = text.size();
    while (first < last && std::isspace(static_cast<unsigned char>(text[first]))) ++first;
    while (last > first && std::isspace(static_cast<unsigned char>(text[last - 1]))) --last;
    return text.substr(first, last - first);
}

}  // namespace

std::string sha256Hex(const std::string& data) {
    Sha256 hasher;
    hasher.update(reinterpret_cast<const unsigned char*>(data.data()), data.size());
    return hasher.hex();
}

FileHashResult sha256File(const std::string& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) throw std::runtime_error("The file could not be opened for reading.");

    Sha256 hasher;
    FileHashResult result;
    std::array<char, 64 * 1024> buffer{};
    while (input) {
        input.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
        const std::streamsize got = input.gcount();
        if (got <= 0) break;
        hasher.update(reinterpret_cast<const unsigned char*>(buffer.data()),
                      static_cast<std::size_t>(got));
        result.bytes += static_cast<unsigned long long>(got);
    }
    if (input.bad()) throw std::runtime_error("The file could not be read completely.");
    result.sha256 = hasher.hex();
    return result;
}

bool isSha256Hex(const std::string& text) {
    if (text.size() != 64) return false;
    for (unsigned char c : text)
        if (!isHexDigit(c)) return false;
    return true;
}

std::string verifyHash(const std::string& actual, const std::string& reference) {
    std::string wanted = trimmed(reference);
    for (char& c : wanted) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    if (wanted.empty()) return "NO REFERENCE GIVEN";
    if (!isSha256Hex(wanted))
        throw std::invalid_argument("A reference hash has exactly 64 hexadecimal characters.");
    return wanted == actual ? "MATCH" : "MISMATCH";
}
