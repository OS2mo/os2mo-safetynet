# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from httpx import AsyncClient
from more_itertools import one

from tests.integration.reports import download_report
from tests.integration.reports import read_local_report
from tests.integration.reports import remove_local_reports
from tests.integration.reports import remove_reports

# End-to-end tests against a real SFTP server (the `sftp` service in
# docker-compose.yml): generate the reports, upload them via SFTP, then fetch
# them back and verify their contents. See the repo AGENTS.md for how to run.


@pytest.mark.integration_test
async def test_e2e_generate_upload_and_download_via_sftp(
    test_client: AsyncClient, opus_tree: UUID
) -> None:
    """Generate the ADM engagement report, upload it to a real SFTP server via
    ``POST /trigger`` (no skip_upload), then download it again and verify it."""
    # Arrange
    ou = str(opus_tree)

    # Act: a real run uploads the CSV reports to the SFTP server.
    response = await test_client.post(
        "/trigger", params={"adm_unit_uuid": ou, "only_adm_org": True}
    )
    assert response.status_code == 200, response.text

    # Assert: the uploaded engagement report can be downloaded and matches.
    row = one(download_report("adm-engagements.csv"))
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
async def test_download_adm_reports_from_sftp(
    test_client: AsyncClient, opus_tree: UUID
) -> None:
    """`POST /download` fetches the uploaded ADM reports back into /tmp."""
    # Arrange: a real run uploads the two ADM reports.
    response = await test_client.post(
        "/trigger", params={"adm_unit_uuid": str(opus_tree), "only_adm_org": True}
    )
    assert response.status_code == 200, response.text

    # Act
    response = await test_client.post("/download", params={"only_adm_org": True})
    assert response.status_code == 200, response.text

    # Assert: the local names are prefixed, so a `skip_upload` run's reports
    # cannot be overwritten.
    assert response.json() == {
        "adm-engagements.csv": "/tmp/downloaded-adm-engagements.csv",
        "adm-org-units.csv": "/tmp/downloaded-adm-org-units.csv",
    }

    row = one(read_local_report("downloaded-adm-engagements.csv"))
    assert row["Medarbejdernummer"] == "12345"
    assert row["CPR"] == "2512480001"
    assert row["Afdelingskode"] == str(opus_tree)

    ou_row = one(read_local_report("downloaded-adm-org-units.csv"))
    assert ou_row["Afdelingsnavn"] == "SafetyNet OPUS"

    remove_reports("adm-engagements.csv", "adm-org-units.csv")


@pytest.mark.integration_test
async def test_download_includes_med_reports(
    test_client: AsyncClient, opus_tree: UUID, med_tree: UUID
) -> None:
    """Without `only_adm_org`, all four reports are downloaded."""
    # Arrange
    response = await test_client.post(
        "/trigger",
        params={"adm_unit_uuid": str(opus_tree), "med_unit_uuid": str(med_tree)},
    )
    assert response.status_code == 200, response.text

    # Act
    response = await test_client.post("/download")
    assert response.status_code == 200, response.text

    # Assert
    assert response.json() == {
        "adm-engagements.csv": "/tmp/downloaded-adm-engagements.csv",
        "adm-org-units.csv": "/tmp/downloaded-adm-org-units.csv",
        "med-associations.csv": "/tmp/downloaded-med-associations.csv",
        "med-org-units.csv": "/tmp/downloaded-med-org-units.csv",
    }

    ass_rows = read_local_report("downloaded-med-associations.csv")
    assert [row["Hverv"] for row in ass_rows] == [
        "TR",
        "næstformand",
        "TR",
        "næstformand",
    ]
    ou_rows = read_local_report("downloaded-med-org-units.csv")
    assert [row["Afdelingsnavn"] for row in ou_rows] == ["SafetyNet MED", "MED child"]

    remove_local_reports(
        "downloaded-adm-engagements.csv", "downloaded-adm-org-units.csv"
    )
    remove_reports(
        "adm-engagements.csv",
        "adm-org-units.csv",
        "med-associations.csv",
        "med-org-units.csv",
    )


@pytest.mark.integration_test
@pytest.mark.envvar({"SAFETYNET_SFTP": "null"})
async def test_download_requires_sftp_settings(test_client: AsyncClient) -> None:
    """Downloading without SFTP settings fails rather than silently doing nothing."""
    response = await test_client.post("/download")
    assert response.status_code == 500
