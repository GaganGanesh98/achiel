"""German private university domains missing from the Hipo list."""

from __future__ import annotations

STUDENT_PREFIXES = ("stud.", "student.", "students.")

GERMAN_PRIVATE_UNI_DOMAINS: tuple[str, ...] = (
    "srh-university.de",
    "srh-hochschule-berlin.de",
    "srh-hochschule-heidelberg.de",
    "srh-fernhochschule.de",
    "iu.org",
    "iubh.de",
    "gisma.com",
    "code.berlin",
    "hertie-school.org",
    "esmt.berlin",
    "whu.edu",
    "frankfurt-school.de",
    "zeppelin-university.de",
    "bard-college-berlin.de",
    "jacobs-university.de",
    "constructor.university",
    "hochschule-fresenius.de",
    "fom.de",
    "macromedia-fachhochschule.de",
    "hmkw.de",
)


def german_private_domains_with_variants() -> set[str]:
    """Base domains plus stud./student./students. subdomain variants."""
    domains: set[str] = set()
    for raw in GERMAN_PRIVATE_UNI_DOMAINS:
        base = raw.lower().strip()
        if not base:
            continue
        domains.add(base)
        for prefix in STUDENT_PREFIXES:
            domains.add(f"{prefix}{base}")
    return domains
