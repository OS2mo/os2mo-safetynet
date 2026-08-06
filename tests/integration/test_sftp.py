# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import csv
from io import BytesIO
from io import StringIO
from uuid import UUID

import pytest
from httpx import AsyncClient
from more_itertools import one

from safetynet.config import SafetyNetSettings
from safetynet.safetynet import sftp_client

# End-to-end test against a real SFTP server (the `sftp` service in
# docker-compose.yml): generate a report, upload it via SFTP, then download it
# again and verify its contents. See the repo AGENTS.md for how to run.


def _download_report(name: str) -> list[dict[str, str]]:
    """Download a report from the SFTP server and parse it with DictReader.

    Uses the same SFTP settings the app uploads with. The reports use ``||`` as
    delimiter; csv only supports single-character delimiters, so collapse ``||``
    to ``|`` before parsing.
    """
    sftp = SafetyNetSettings().safetynet_sftp
    assert sftp is not None, "SFTP must be configured for the e2e test"

    buffer = BytesIO()
    with sftp_client(
        sftp.hostname, sftp.port, sftp.username, sftp.password.get_secret_value()
    ) as client:
        client.getfo(name, buffer)
        # Clean up so the assertion always reflects the current run.
        client.remove(name)

    content = buffer.getvalue().decode("utf-8").replace("||", "|")
    return list(csv.DictReader(StringIO(content), delimiter="|"))


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
    row = one(_download_report("adm-engagements.csv"))
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
