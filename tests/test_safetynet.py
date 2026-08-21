# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import csv
from io import StringIO
from uuid import UUID

import pytest

from safetynet.safetynet import AdmEngRow
from safetynet.safetynet import AdmOuRow
from safetynet.safetynet import MedAssRow
from safetynet.safetynet import MedOuRow
from safetynet.safetynet import _remove_sd_user_key_prefix
from safetynet.safetynet import adm_eng_rows_to_csv_lines
from safetynet.safetynet import adm_ou_rows_to_csv_lines
from safetynet.safetynet import med_ass_rows_to_csv_lines
from safetynet.safetynet import med_ou_rows_to_csv_lines

ORG_UNIT = UUID("9d1af806-f4d6-44e2-a001-a5deb3aa6703")


def _parse_csv(lines: list[str]) -> list[dict[str, str]]:
    """Parse SafetyNet CSV lines into row dicts with ``csv.DictReader``.

    The reports use ``||`` as delimiter; csv only supports single-character
    delimiters, so collapse ``||`` to ``|`` before parsing.
    """
    content = "".join(lines).replace("||", "|")
    return list(csv.DictReader(StringIO(content), delimiter="|"))


def _adm_eng_row(manager_cpr: str = "") -> AdmEngRow:
    return AdmEngRow(
        person_user_key="12345",
        cpr="0101011255",
        first_name="Bruce",
        last_name="Lee",
        email="bruce@kung.fu",
        org_unit=ORG_UNIT,
        eng_start="2021-10-22",
        eng_end="2025-09-30",
        manager_eng_user_key="54321",
        manager_cpr=manager_cpr,
        username="bruce",
        job_function="Kung Fu Master",
    )


def test_adm_eng_rows_to_csv_lines_without_manager_cpr() -> None:
    lines = adm_eng_rows_to_csv_lines([_adm_eng_row()], include_manager_cpr=False)
    assert _parse_csv(lines) == [
        {
            "Medarbejdernummer": "12345",
            "CPR": "0101011255",
            "Fornavn": "Bruce",
            "Efternavn": "Lee",
            "Mail": "bruce@kung.fu",
            "Afdelingskode": "9d1af806-f4d6-44e2-a001-a5deb3aa6703",
            "Startdato": "2021-10-22",
            "Slutdato": "2025-09-30",
            "LedersMedarbejdernummer": "54321",
            "Brugernavn": "bruce",
            "Titel": "Kung Fu Master",
            "Faggruppe": "Kung Fu Master",
        }
    ]


def test_adm_eng_rows_to_csv_lines_with_manager_cpr() -> None:
    lines = adm_eng_rows_to_csv_lines(
        [_adm_eng_row(manager_cpr="2001011299")], include_manager_cpr=True
    )
    assert _parse_csv(lines) == [
        {
            "Medarbejdernummer": "12345",
            "CPR": "0101011255",
            "Fornavn": "Bruce",
            "Efternavn": "Lee",
            "Mail": "bruce@kung.fu",
            "Afdelingskode": "9d1af806-f4d6-44e2-a001-a5deb3aa6703",
            "Startdato": "2021-10-22",
            "Slutdato": "2025-09-30",
            "LedersMedarbejdernummer": "54321",
            "LedersCPR": "2001011299",
            "Brugernavn": "bruce",
            "Titel": "Kung Fu Master",
            "Faggruppe": "Kung Fu Master",
        }
    ]


def test_adm_ou_rows_to_csv_lines() -> None:
    row = AdmOuRow(
        name="Some name",
        uuid=ORG_UNIT,
        parent=UUID("06f200ae-a05e-4fb3-91a4-9f16a0fc0b98"),
        pnumber="1234567890",
        related_units=[
            UUID("626ab928-a76f-46ae-bc8f-2402deb65236"),
            UUID("18b8b97d-946d-4948-a334-0582935f7c5c"),
        ],
    )
    assert _parse_csv(adm_ou_rows_to_csv_lines([row])) == [
        {
            "Afdelingsnavn": "Some name",
            "Afdelingskode": "9d1af806-f4d6-44e2-a001-a5deb3aa6703",
            "Forældreafdelingskode": "06f200ae-a05e-4fb3-91a4-9f16a0fc0b98",
            "Pnummer": "1234567890",
            "Arbejdsmiljøorganisationkode": (
                "626ab928-a76f-46ae-bc8f-2402deb65236,"
                "18b8b97d-946d-4948-a334-0582935f7c5c"
            ),
        }
    ]


def test_med_ass_rows_to_csv_lines() -> None:
    row = MedAssRow(
        cpr="0101011234",
        org_unit=ORG_UNIT,
        ass_start="2022-01-06",
        ass_end="",
        role="AMR",
        main_org="Ej relevant",
    )
    assert _parse_csv(med_ass_rows_to_csv_lines([row])) == [
        {
            "CPR": "0101011234",
            "Afdelingskode": "9d1af806-f4d6-44e2-a001-a5deb3aa6703",
            "Startdato": "2022-01-06",
            "Slutdato": "",
            "Hverv": "AMR",
            "Hovedorganisation": "Ej relevant",
        }
    ]


def test_med_ou_rows_to_csv_lines() -> None:
    row = MedOuRow(name="Some name", uuid=ORG_UNIT, parent=None)
    assert _parse_csv(med_ou_rows_to_csv_lines([row])) == [
        {
            "Afdelingsnavn": "Some name",
            "Afdelingskode": "9d1af806-f4d6-44e2-a001-a5deb3aa6703",
            "Forældreafdelingskode": "",
        }
    ]


@pytest.mark.parametrize(
    ("user_key", "expected"),
    [
        # No prefix
        ("12345", "12345"),
        # SD InstitutionIdentifier prefix
        ("XY-12345", "12345"),
        ("AB-987654", "987654"),
        # UUID should be returned unchanged
        (
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400-e29b-41d4-a716-446655440000",
        ),
        # Multiple hyphens (not a UUID) should be returned unchanged
        ("ABC-123-456", "ABC-123-456"),
        ("", ""),
    ],
)
def test_remove_sd_user_key_prefix(user_key: str, expected: str) -> None:
    assert _remove_sd_user_key_prefix(user_key) == expected
