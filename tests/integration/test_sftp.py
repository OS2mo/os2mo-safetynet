# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import pytest
from httpx import AsyncClient
from more_itertools import one

from tests.integration.reports import download_report

# End-to-end test against a real SFTP server (the `sftp` service in
# docker-compose.yml): generate a report, upload it via SFTP, then download it
# again and verify its contents. See the repo AGENTS.md for how to run.


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
