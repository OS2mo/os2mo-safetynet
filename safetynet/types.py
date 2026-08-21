# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import NewType

# The MO GraphQL `CPR` scalar. Referenced from the ariadne-codegen config in
# pyproject.toml (`[tool.ariadne-codegen.scalars.CPR]`) so the generated client
# maps `cpr_number` fields to this type instead of a plain string.
CPRNumber = NewType("CPRNumber", str)
