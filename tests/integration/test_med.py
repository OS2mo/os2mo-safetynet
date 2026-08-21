# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from httpx import AsyncClient

from tests.integration.reports import download_report
from tests.integration.reports import read_local_report
from tests.integration.reports import remove_local_reports
from tests.integration.reports import remove_reports

# Integration tests for the MED organisation: the association
# report and the MED org unit report. See the repo AGENTS.md for how to run.
#
# `generate_reports` always produces the two ADM reports as well, so these tests
# seed an ADM tree (`opus_tree`) alongside the MED one and trigger with both
# roots. The MED reports are uploaded over real SFTP rather than written to
# /tmp, which exercises the upload path end to end.


@pytest.mark.integration_test
async def test_med_association_and_org_unit_reports(
    test_client: AsyncClient, opus_tree: UUID, med_tree: UUID
) -> None:
    """Both MED reports are generated, uploaded and correct.

    The MED tree is a root unit with an association carrying a trade union, and
    a child unit with one that does not. Both associations use the composite
    "TR, næstformand" role, which must be split into one row per role (Redmine
    case #63407), so four association rows are expected in total.
    """
    # Act
    response = await test_client.post(
        "/trigger",
        params={
            "adm_unit_uuid": str(opus_tree),
            "med_unit_uuid": str(med_tree),
        },
    )
    assert response.status_code == 200, response.text

    # Assert: the summary counts both MED reports.
    assert response.json() == {
        "adm_engagements": 1,
        "adm_org_units": 1,
        "med_associations": 4,
        "med_org_units": 2,
    }

    # Assert: the report follows the traversal (root then child), and each
    # association's composite role is split in the order it is written.
    ass_rows = download_report("med-associations.csv")
    root_tr, root_naestformand, child_tr, child_naestformand = ass_rows

    assert root_tr["CPR"] == "2512480020"
    assert root_tr["Afdelingskode"] == str(med_tree)
    assert root_tr["Startdato"] == "1990-01-01"
    assert root_tr["Slutdato"] == ""
    assert root_tr["Hverv"] == "TR"
    assert root_tr["Hovedorganisation"] == "LO"

    # The composite role produces a second row for the same association.
    assert root_naestformand["CPR"] == "2512480020"
    assert root_naestformand["Afdelingskode"] == str(med_tree)
    assert root_naestformand["Hverv"] == "næstformand"
    assert root_naestformand["Hovedorganisation"] == "LO"

    # The child's association has no trade union, so Hovedorganisation is empty.
    child_unit = child_tr["Afdelingskode"]
    assert child_unit != str(med_tree)
    assert child_tr["CPR"] == "2512480021"
    assert child_tr["Hverv"] == "TR"
    assert child_tr["Hovedorganisation"] == ""
    assert child_naestformand["CPR"] == "2512480021"
    assert child_naestformand["Hverv"] == "næstformand"
    assert child_naestformand["Hovedorganisation"] == ""

    # Assert: the MED org unit report covers the whole tree, root first.
    ou_rows = download_report("med-org-units.csv")
    root_row, child_row = ou_rows

    assert root_row["Afdelingsnavn"] == "SafetyNet MED"
    assert root_row["Afdelingskode"] == str(med_tree)
    assert root_row["Forældreafdelingskode"] == ""

    assert child_row["Afdelingsnavn"] == "MED child"
    assert child_row["Afdelingskode"] == child_unit
    assert child_row["Forældreafdelingskode"] == str(med_tree)

    remove_reports("adm-engagements.csv", "adm-org-units.csv")


@pytest.mark.integration_test
async def test_med_reports_written_locally_with_skip_upload(
    test_client: AsyncClient, opus_tree: UUID, med_tree: UUID
) -> None:
    """`skip_upload` writes the MED reports to /tmp instead of uploading them."""
    # Act
    response = await test_client.post(
        "/trigger",
        params={
            "adm_unit_uuid": str(opus_tree),
            "med_unit_uuid": str(med_tree),
            "skip_upload": True,
        },
    )
    assert response.status_code == 200, response.text

    # Assert
    ass_rows = read_local_report("med-associations.csv")
    assert [row["Hverv"] for row in ass_rows] == [
        "TR",
        "næstformand",
        "TR",
        "næstformand",
    ]
    ou_rows = read_local_report("med-org-units.csv")
    assert [row["Afdelingsnavn"] for row in ou_rows] == ["SafetyNet MED", "MED child"]

    remove_local_reports("adm-engagements.csv", "adm-org-units.csv")


@pytest.mark.integration_test
async def test_med_unit_uuid_required_unless_only_adm_org(
    test_client: AsyncClient, opus_tree: UUID
) -> None:
    """Without `only_adm_org`, a MED root is required (none is configured)."""
    response = await test_client.post(
        "/trigger", params={"adm_unit_uuid": str(opus_tree), "skip_upload": True}
    )
    assert response.status_code == 500
