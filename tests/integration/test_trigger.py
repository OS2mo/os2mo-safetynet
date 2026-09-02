# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os
from operator import itemgetter
from uuid import UUID

import pytest
from httpx import AsyncClient
from more_itertools import one

from tests.integration.conftest import TO_DATE_INCLUSIVE
from tests.integration.reports import read_local_report
from tests.integration.reports import remove_local_reports

# These integration tests run against a live OS2mo stack (see the repo AGENTS.md:
# run them with `docker compose run --rm safetynet pytest -m integration_test`,
# never `pytest` directly on the host). The FastRAMQPI integration fixtures reset
# MO to an empty database around every test, so each test seeds everything it
# needs (root organisation, facets and classes, and its own small ADM tree at the
# root of the org-unit tree) and the seeded data is isolated and cleaned up.
#
# Every test asserts every column of every row, mirroring the use cases of the
# original mock-based unit tests: OPUS direct manager, OPUS "manager is the
# employee" -> parent manager, SD via engagement-type fallback, SD engagement
# coupling precedence, SD prefix stripping, the CSV format, and the LedersCPR
# column.
#
# All seeded engagements use the fixed validity start FROM_DATE (1990-01-01) and
# no end date, and the "Ninja" job function; employees have no AD-Email address
# (so the Mail/Brugernavn columns are empty).


async def _trigger_adm(test_client: AsyncClient, adm_unit_uuid: UUID) -> dict:
    response = await test_client.post(
        "/trigger",
        params={
            "adm_unit_uuid": str(adm_unit_uuid),
            "skip_upload": True,
            "only_adm_org": True,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.integration_test
async def test_opus_manager_not_the_employee(
    test_client: AsyncClient, opus_tree: UUID
) -> None:
    """OPUS: person_user_key is verbatim; manager number is the OU manager's key."""
    # Arrange
    ou = str(opus_tree)

    # Act
    summary = await _trigger_adm(test_client, opus_tree)

    # Assert
    assert summary == {
        "adm_engagements": 1,
        "adm_org_units": 1,
        "med_associations": 0,
        "med_org_units": 0,
    }
    row = one(read_local_report("adm-engagements.csv"))
    remove_local_reports("adm-org-units.csv")
    assert row["Medarbejdernummer"] == "12345"
    assert row["CPR"] == "2512480001"
    assert row["Fornavn"] == "Opus"
    assert row["Efternavn"] == "Employee"
    assert row["Mail"] == ""
    assert row["Afdelingskode"] == ou
    assert row["Startdato"] == "1990-01-01"
    assert row["Slutdato"] == ""
    assert row["LedersMedarbejdernummer"] == "54321"
    assert row["Brugernavn"] == ""
    assert row["Titel"] == "Ninja"
    assert row["Faggruppe"] == "Ninja"


@pytest.mark.integration_test
async def test_opus_manager_is_the_employee_uses_parent_manager(
    test_client: AsyncClient, opus_self_managed_tree: UUID
) -> None:
    """OPUS: when the unit's manager is the employee, fall back to the parent
    unit's manager (54321)."""
    # Arrange
    ou = str(opus_self_managed_tree)

    # Act
    await _trigger_adm(test_client, opus_self_managed_tree)

    # Assert
    row = one(read_local_report("adm-engagements.csv"))
    remove_local_reports("adm-org-units.csv")
    assert row["Medarbejdernummer"] == "12345"
    assert row["CPR"] == "2512480006"
    assert row["Fornavn"] == "Opus"
    assert row["Efternavn"] == "SelfManager"
    assert row["Mail"] == ""
    assert row["Afdelingskode"] == ou
    assert row["Startdato"] == "1990-01-01"
    assert row["Slutdato"] == ""
    assert row["LedersMedarbejdernummer"] == "54321"
    assert row["Brugernavn"] == ""
    assert row["Titel"] == "Ninja"
    assert row["Faggruppe"] == "Ninja"


@pytest.mark.integration_test
@pytest.mark.envvar({"SOURCE_SYSTEM": "sd"})
async def test_sd_manager_via_engagement_response(
    test_client: AsyncClient, sd_tree: UUID
) -> None:
    """SD: prefix stripped; manager number resolved via the manager's engagement.
    The manager also has their own engagement row (with no manager)."""
    # Arrange
    ou = str(sd_tree)

    # Act
    await _trigger_adm(test_client, sd_tree)

    # Assert
    employee, manager = sorted(
        read_local_report("adm-engagements.csv"), key=itemgetter("Medarbejdernummer")
    )
    remove_local_reports("adm-org-units.csv")

    assert employee["Medarbejdernummer"] == "55501"
    assert employee["CPR"] == "2512480003"
    assert employee["Fornavn"] == "Sd"
    assert employee["Efternavn"] == "Employee"
    assert employee["Mail"] == ""
    assert employee["Afdelingskode"] == ou
    assert employee["Startdato"] == "1990-01-01"
    assert employee["Slutdato"] == ""
    assert employee["LedersMedarbejdernummer"] == "55502"
    assert employee["Brugernavn"] == ""
    assert employee["Titel"] == "Ninja"
    assert employee["Faggruppe"] == "Ninja"

    assert manager["Medarbejdernummer"] == "55502"
    assert manager["CPR"] == "2512480004"
    assert manager["Fornavn"] == "Sd"
    assert manager["Efternavn"] == "Manager"
    assert manager["Mail"] == ""
    assert manager["Afdelingskode"] == ou
    assert manager["Startdato"] == "1990-01-01"
    assert manager["Slutdato"] == ""
    assert manager["LedersMedarbejdernummer"] == ""
    assert manager["Brugernavn"] == ""
    assert manager["Titel"] == "Ninja"
    assert manager["Faggruppe"] == "Ninja"


@pytest.mark.integration_test
@pytest.mark.envvar({"SOURCE_SYSTEM": "sd"})
async def test_sd_manager_via_engagement_type_fallback(
    test_client: AsyncClient, sd_fallback_tree: UUID
) -> None:
    """SD: with no linked manager engagement, resolve via the allowed engagement
    types.

    The manager holds two engagements, "fuldtid" (allowed) and "timelønnet"
    (not), so the reported manager number is only unambiguous because the
    disallowed one is filtered out.
    """
    # Arrange
    ou = str(sd_fallback_tree)

    # Act
    await _trigger_adm(test_client, sd_fallback_tree)

    # Assert
    employee, *_ = sorted(
        read_local_report("adm-engagements.csv"), key=itemgetter("Medarbejdernummer")
    )
    remove_local_reports("adm-org-units.csv")

    # The allowed-type engagement wins over the manager's "timelønnet" one.
    assert employee["Medarbejdernummer"] == "70001"
    assert employee["CPR"] == "2512480007"
    assert employee["Fornavn"] == "Sd"
    assert employee["Efternavn"] == "FbEmployee"
    assert employee["Mail"] == ""
    assert employee["Afdelingskode"] == ou
    assert employee["Startdato"] == "1990-01-01"
    assert employee["Slutdato"] == ""
    assert employee["LedersMedarbejdernummer"] == "70002"
    assert employee["Brugernavn"] == ""
    assert employee["Titel"] == "Ninja"
    assert employee["Faggruppe"] == "Ninja"


@pytest.mark.integration_test
@pytest.mark.envvar({"SOURCE_SYSTEM": "sd"})
async def test_sd_manager_engagement_coupling_takes_precedence(
    test_client: AsyncClient, sd_coupling_tree: UUID
) -> None:
    """SD: with multiple candidate manager engagements, the linked engagement
    (engagement_response) wins over the ambiguous type fallback. The manager's two
    engagements produce two rows (each with no manager)."""
    # Arrange
    ou = str(sd_coupling_tree)

    # Act
    await _trigger_adm(test_client, sd_coupling_tree)

    # Assert
    employee, manager_eng_1, manager_eng_2 = sorted(
        read_local_report("adm-engagements.csv"), key=itemgetter("Medarbejdernummer")
    )
    remove_local_reports("adm-org-units.csv")

    assert employee["Medarbejdernummer"] == "80001"
    assert employee["CPR"] == "2512480009"
    assert employee["Fornavn"] == "Sd"
    assert employee["Efternavn"] == "CplEmployee"
    assert employee["Mail"] == ""
    assert employee["Afdelingskode"] == ou
    assert employee["Startdato"] == "1990-01-01"
    assert employee["Slutdato"] == ""
    assert employee["LedersMedarbejdernummer"] == "80002"
    assert employee["Brugernavn"] == ""
    assert employee["Titel"] == "Ninja"
    assert employee["Faggruppe"] == "Ninja"

    assert manager_eng_1["Medarbejdernummer"] == "80002"
    assert manager_eng_1["CPR"] == "2512480010"
    assert manager_eng_1["Fornavn"] == "Sd"
    assert manager_eng_1["Efternavn"] == "CplManager"
    assert manager_eng_1["Mail"] == ""
    assert manager_eng_1["Afdelingskode"] == ou
    assert manager_eng_1["Startdato"] == "1990-01-01"
    assert manager_eng_1["Slutdato"] == ""
    assert manager_eng_1["LedersMedarbejdernummer"] == ""
    assert manager_eng_1["Brugernavn"] == ""
    assert manager_eng_1["Titel"] == "Ninja"
    assert manager_eng_1["Faggruppe"] == "Ninja"

    assert manager_eng_2["Medarbejdernummer"] == "80003"
    assert manager_eng_2["CPR"] == "2512480010"
    assert manager_eng_2["Fornavn"] == "Sd"
    assert manager_eng_2["Efternavn"] == "CplManager"
    assert manager_eng_2["Mail"] == ""
    assert manager_eng_2["Afdelingskode"] == ou
    assert manager_eng_2["Startdato"] == "1990-01-01"
    assert manager_eng_2["Slutdato"] == ""
    assert manager_eng_2["LedersMedarbejdernummer"] == ""
    assert manager_eng_2["Brugernavn"] == ""
    assert manager_eng_2["Titel"] == "Ninja"
    assert manager_eng_2["Faggruppe"] == "Ninja"


@pytest.mark.integration_test
@pytest.mark.envvar({"INCLUDE_MANAGER_CPR": "true"})
async def test_include_manager_cpr_adds_lederscpr_column(
    test_client: AsyncClient, opus_tree: UUID
) -> None:
    """include_manager_cpr adds the LedersCPR column with the manager's CPR."""
    # Arrange
    ou = str(opus_tree)

    # Act
    await _trigger_adm(test_client, opus_tree)

    # Assert
    row = one(read_local_report("adm-engagements.csv"))
    remove_local_reports("adm-org-units.csv")
    assert row["Medarbejdernummer"] == "12345"
    assert row["CPR"] == "2512480001"
    assert row["Fornavn"] == "Opus"
    assert row["Efternavn"] == "Employee"
    assert row["Mail"] == ""
    assert row["Afdelingskode"] == ou
    assert row["Startdato"] == "1990-01-01"
    assert row["Slutdato"] == ""
    assert row["LedersMedarbejdernummer"] == "54321"
    assert row["LedersCPR"] == "2512480002"
    assert row["Brugernavn"] == ""
    assert row["Titel"] == "Ninja"
    assert row["Faggruppe"] == "Ninja"


@pytest.mark.integration_test
async def test_adm_org_unit_report(test_client: AsyncClient, opus_tree: UUID) -> None:
    """The ADM OU report for the seeded root unit (no parent, pnumber or related
    units)."""
    # Arrange
    ou = str(opus_tree)

    # Act
    await _trigger_adm(test_client, opus_tree)

    # Assert
    row = one(read_local_report("adm-org-units.csv"))
    remove_local_reports("adm-engagements.csv")
    assert row["Afdelingsnavn"] == "SafetyNet OPUS"
    assert row["Afdelingskode"] == ou
    assert row["Forældreafdelingskode"] == ""
    assert row["Pnummer"] == ""
    assert row["Arbejdsmiljøorganisationkode"] == ""


@pytest.mark.integration_test
async def test_opus_unit_without_manager(
    test_client: AsyncClient, opus_unmanaged_tree: UUID
) -> None:
    """OPUS: a unit with no manager leaves the manager engagement number empty."""
    # Act
    await _trigger_adm(test_client, opus_unmanaged_tree)

    # Assert
    row = one(read_local_report("adm-engagements.csv"))
    remove_local_reports("adm-org-units.csv")
    assert row["Medarbejdernummer"] == "12345"
    assert row["CPR"] == "2512480011"
    assert row["Efternavn"] == "Unmanaged"
    assert row["LedersMedarbejdernummer"] == ""


@pytest.mark.integration_test
async def test_adm_tree_is_traversed_recursively(
    test_client: AsyncClient, opus_nested_tree: UUID
) -> None:
    """Processing a unit descends into its children, reporting both levels."""
    # Arrange
    parent = str(opus_nested_tree)

    # Act
    summary = await _trigger_adm(test_client, opus_nested_tree)

    # Assert
    assert summary == {
        "adm_engagements": 2,
        "adm_org_units": 2,
        "med_associations": 0,
        "med_org_units": 0,
    }

    parent_eng, child_eng = sorted(
        read_local_report("adm-engagements.csv"), key=itemgetter("Medarbejdernummer")
    )
    assert parent_eng["Medarbejdernummer"] == "11111"
    assert parent_eng["Efternavn"] == "ParentEmployee"
    assert parent_eng["Afdelingskode"] == parent
    assert parent_eng["LedersMedarbejdernummer"] == "54321"

    assert child_eng["Medarbejdernummer"] == "22222"
    assert child_eng["Efternavn"] == "ChildEmployee"
    child_unit = child_eng["Afdelingskode"]
    assert child_unit != parent
    # The child unit has no manager of its own, so it inherits the parent's.
    assert child_eng["LedersMedarbejdernummer"] == "54321"

    # The OU report follows the traversal: the parent, then its child.
    parent_ou, child_ou = read_local_report("adm-org-units.csv")
    assert parent_ou["Afdelingsnavn"] == "OPUS nested parent"
    assert parent_ou["Afdelingskode"] == parent
    assert parent_ou["Forældreafdelingskode"] == ""
    assert child_ou["Afdelingsnavn"] == "OPUS nested child"
    assert child_ou["Afdelingskode"] == child_unit
    assert child_ou["Forældreafdelingskode"] == parent


@pytest.mark.integration_test
@pytest.mark.envvar({"SOURCE_SYSTEM": "sd"})
async def test_sd_ambiguous_manager_engagements_without_coupling(
    test_client: AsyncClient, sd_ambiguous_tree: UUID
) -> None:
    """SD: two candidate manager engagements and no coupling is unresolvable, so
    the manager engagement number is left empty."""
    # Act
    await _trigger_adm(test_client, sd_ambiguous_tree)

    # Assert
    employee, _, _ = sorted(
        read_local_report("adm-engagements.csv"), key=itemgetter("Medarbejdernummer")
    )
    remove_local_reports("adm-org-units.csv")
    assert employee["Medarbejdernummer"] == "90001"
    assert employee["CPR"] == "2512480015"
    assert employee["Efternavn"] == "AmbEmployee"
    assert employee["LedersMedarbejdernummer"] == ""


@pytest.mark.integration_test
@pytest.mark.envvar({"SAFETYNET_SFTP": "null"})
async def test_upload_is_skipped_when_sftp_is_not_configured(
    test_client: AsyncClient, opus_tree: UUID
) -> None:
    """With no SFTP settings, a real (non-`skip_upload`) run logs and moves on
    rather than failing."""
    # Act
    response = await test_client.post(
        "/trigger", params={"adm_unit_uuid": str(opus_tree), "only_adm_org": True}
    )

    # Assert
    assert response.status_code == 200, response.text
    assert response.json() == {
        "adm_engagements": 1,
        "adm_org_units": 1,
        "med_associations": 0,
        "med_org_units": 0,
    }
    # Nothing was written locally either, since this was not a skip_upload run.
    assert not os.path.exists("/tmp/adm-engagements.csv")
    assert not os.path.exists("/tmp/adm-org-units.csv")


@pytest.mark.integration_test
async def test_engagement_end_date_is_the_last_valid_day(
    test_client: AsyncClient, opus_closed_tree: UUID
) -> None:
    """Slutdato is the last day the engagement is valid.

    MO returns `validity.to` as an exclusive end from GraphQL v29 on, so the raw
    value is a day later than the report must show.
    """
    # Act
    await _trigger_adm(test_client, opus_closed_tree)

    # Assert
    row = one(read_local_report("adm-engagements.csv"))
    remove_local_reports("adm-org-units.csv")
    assert row["Medarbejdernummer"] == "12345"
    assert row["CPR"] == "2512480017"
    assert row["Startdato"] == "1990-01-01"
    assert row["Slutdato"] == TO_DATE_INCLUSIVE
