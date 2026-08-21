# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Helpers for reading back the reports a triggered run produced.

A run either uploads its reports over SFTP or, with ``skip_upload``, writes them
to /tmp; there is a reader and a remover for each. The readers remove what they
read, so an assertion always reflects the current run rather than a leftover.
"""

import csv
from collections.abc import Iterator
from contextlib import contextmanager
from io import BytesIO
from io import StringIO
from pathlib import Path

from paramiko import SFTPClient

from safetynet.config import SafetyNetSettings
from safetynet.safetynet import sftp_client


def _parse_csv(content: str) -> list[dict[str, str]]:
    """Parse a report with ``csv.DictReader``.

    The reports use ``||`` as delimiter; csv only supports single-character
    delimiters, so collapse ``||`` to ``|`` before parsing.
    """
    return list(csv.DictReader(StringIO(content.replace("||", "|")), delimiter="|"))


@contextmanager
def _sftp() -> Iterator[SFTPClient]:
    """Connect to the SFTP server with the settings the app uploads with."""
    sftp = SafetyNetSettings().safetynet_sftp
    assert sftp is not None, "SFTP must be configured for the e2e tests"
    with sftp_client(
        sftp.hostname, sftp.port, sftp.username, sftp.password.get_secret_value()
    ) as client:
        yield client


def download_report(name: str) -> list[dict[str, str]]:
    """Download (and remove) an uploaded report from the SFTP server."""
    buffer = BytesIO()
    with _sftp() as client:
        client.getfo(name, buffer)
        client.remove(name)
    return _parse_csv(buffer.getvalue().decode("utf-8"))


def remove_reports(*names: str) -> None:
    """Remove uploaded reports that a test does not assert on."""
    with _sftp() as client:
        for name in names:
            client.remove(name)


def read_local_report(name: str) -> list[dict[str, str]]:
    """Read (and remove) a report written to /tmp by a ``skip_upload`` run."""
    path = Path("/tmp") / name
    content = path.read_text()
    path.unlink()
    return _parse_csv(content)


def remove_local_reports(*names: str) -> None:
    """Remove locally written reports that a test does not assert on."""
    for name in names:
        (Path("/tmp") / name).unlink()
