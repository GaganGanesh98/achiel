from unittest.mock import patch

from app.models.domain import AllowedDomainSource
from app.seed.german_private_unis import german_private_domains_with_variants
from app.services import university_email as uni_email
from tests.conftest import allow_domain


def test_german_private_list_includes_stud_srh_subdomain() -> None:
    domains = german_private_domains_with_variants()
    assert "srh-university.de" in domains
    assert "stud.srh-university.de" in domains


async def test_stud_srh_university_de_allowed_when_manual_seeded(
    db, clean_domain_tables
) -> None:
    await allow_domain(db, "stud.srh-university.de", source=AllowedDomainSource.MANUAL)
    with patch.object(uni_email, "domain_has_mx", return_value=True):
        result = await uni_email.validate_university_email(
            db, "user@stud.srh-university.de", record_pending=False
        )
    assert result.status == "allowed"
