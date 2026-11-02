"""Module 8: IP Address Validator, built on Python's standard ipaddress module."""
import ipaddress

MAX_INPUT = 100


def _invalid(message):
    return {"valid": False, "error": message}


def classify(ip):
    """One plain-language label. The order matters: the most specific kind wins."""
    if ip.is_unspecified:
        return "Unspecified"
    if ip.is_loopback:
        return "Loopback (this computer)"
    if ip.is_link_local:
        return "Link-local"
    if ip.is_multicast:
        return "Multicast"
    if ip.is_private:
        return "Private (not routable on the public internet)"
    if ip.is_global:
        return "Public (global)"
    return "Reserved or special-purpose"


def validate_ip(text):
    """Check an IPv4 or IPv6 address. Bad input returns valid=False, it does not crash."""
    if not isinstance(text, str):
        return _invalid("The address must be text.")
    value = text.strip()
    if not value:
        return _invalid("Enter an IP address.")
    if len(value) > MAX_INPUT:
        return _invalid("That is too long to be an IP address.")
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return _invalid("'%s' is not a valid IPv4 or IPv6 address." % value[:40])

    result = {
        "valid": True,
        "address": str(ip),
        "version": ip.version,
        "classification": classify(ip),
        "is_private": ip.is_private,
        "is_global": ip.is_global,
        "is_loopback": ip.is_loopback,
        "is_link_local": ip.is_link_local,
        "is_multicast": ip.is_multicast,
        "is_reserved": ip.is_reserved,
        "is_unspecified": ip.is_unspecified,
        "reverse_pointer": ip.reverse_pointer,
    }
    if ip.version == 6:
        result["compressed"] = ip.compressed
        result["exploded"] = ip.exploded
        result["ipv4_mapped"] = str(ip.ipv4_mapped) if ip.ipv4_mapped else "none"
    return result
