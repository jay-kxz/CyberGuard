"""Module 6: Password Strength Analyzer.

A HEURISTIC for learning. It scores a sample password out of 100:
    +3 points per character, up to 20 characters   (max 60)
    +10 points for each character type present      (max 40)
    -20 for a repeated pattern (abcabcabc, aaaa)
    -15 for a predictable sequence (abcd, 1234, qwer)
    -10 if fewer than half of the characters are different
    A password on the common-password list is capped at 10.
The password is never stored, printed, logged or returned.
"""
import re
from functools import reduce

MAX_LENGTH = 128

# A set: fast membership tests, no duplicates.
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "123456789", "1234567890", "qwerty", "qwerty123",
    "abc123", "password1", "passw0rd", "111111", "000000", "123123", "admin", "admin123",
    "letmein", "welcome", "iloveyou", "monkey", "dragon", "football", "login", "master",
    "sunshine", "qazwsx",
}

SEQUENCE_SOURCES = ("abcdefghijklmnopqrstuvwxyz", "0123456789", "qwertyuiop", "asdfghjkl", "zxcvbnm")

# A tuple of tuples: (score must be below this limit, rating label).
BANDS = ((30, "Very Weak"), (50, "Weak"), (70, "Fair"), (85, "Strong"), (101, "Very Strong"))

CLASS_LABELS = {"lowercase": "Lowercase letters", "uppercase": "Uppercase letters",
                "digit": "Digits", "special": "Special characters"}


def character_classes(password):
    """Return which character types the password contains."""
    return {
        "lowercase": any(c.islower() for c in password),
        "uppercase": any(c.isupper() for c in password),
        "digit": any(c.isdigit() for c in password),
        "special": any(not c.isalnum() for c in password),
    }


def has_repeated_pattern(password):
    """True if one character or group repeats three or more times in a row."""
    return re.search(r"(.+?)\1{2,}", password) is not None


def has_sequence(password, min_len=4):
    """True if the password holds a run such as abcd, 4321 or qwer (either direction)."""
    lower = password.lower()
    for source in SEQUENCE_SOURCES:
        for i in range(len(source) - min_len + 1):
            chunk = source[i:i + min_len]
            if chunk in lower or chunk[::-1] in lower:
                return True
    return False


def rating_for(score):
    return next(label for limit, label in BANDS if score < limit)


def analyze_password(password):
    """Analyze one sample password. Raises ValueError for unusable input."""
    if not isinstance(password, str):
        raise ValueError("The password must be text.")
    if not password:
        raise ValueError("Enter a password to analyze.")
    if len(password) > MAX_LENGTH:
        raise ValueError("The password is too long (maximum %d characters)." % MAX_LENGTH)

    length = len(password)
    classes = character_classes(password)
    factors = [{"factor": "Length", "detail": "%d characters" % length, "points": min(length, 20) * 3}]
    for key, present in classes.items():
        factors.append({"factor": CLASS_LABELS[key], "detail": "present" if present else "missing",
                        "points": 10 if present else 0})

    repeated, sequence = has_repeated_pattern(password), has_sequence(password)
    low_variety = len(set(password)) * 2 < length
    if repeated:
        factors.append({"factor": "Repeated pattern", "detail": "a character or group repeats 3+ times", "points": -20})
    if sequence:
        factors.append({"factor": "Predictable sequence", "detail": "contains a run like abcd, 1234 or qwer", "points": -15})
    if low_variety:
        factors.append({"factor": "Few different characters", "detail": "under half are different", "points": -10})

    raw = reduce(lambda total, f: total + f["points"], factors, 0)   # add up all the points
    score = max(0, min(100, raw))

    common = password.lower() in COMMON_PASSWORDS
    if common:
        score = min(score, 10)
        factors.append({"factor": "Common password", "detail": "appears on a list of very common passwords", "points": 0})

    missing = list(filter(lambda k: not classes[k], classes))
    suggestions = []
    if length < 12:
        suggestions.append("Use at least 12 characters. Length adds the most strength.")
    suggestions += ["Add %s." % CLASS_LABELS[k].lower() for k in missing]
    if repeated:
        suggestions.append("Avoid repeating the same characters or groups.")
    if sequence:
        suggestions.append("Avoid runs such as abcd, 1234 or qwer.")
    if common:
        suggestions.append("Never use a common password. Try a passphrase of several unrelated words.")
    if not suggestions:
        suggestions.append("Good. Use a different password for every account.")

    return {
        "rating": rating_for(score),
        "score": score,
        "length": length,
        "character_types_present": sum(map(lambda ok: 1 if ok else 0, classes.values())),
        "factors": factors,
        "suggestions": suggestions,
        "note": "A heuristic for learning. It cannot tell whether a password appeared in a data breach.",
    }
