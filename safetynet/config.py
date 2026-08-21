# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from enum import Enum
from uuid import UUID

from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import BaseModel
from pydantic import BaseSettings
from pydantic import Field
from pydantic import SecretStr


class SourceSystem(Enum):
    OPUS = "opus"
    SD = "sd"


class SafetyNetSFTP(BaseModel):
    hostname: str
    port: int
    username: str
    password: SecretStr

    class Config:
        env_nested_delimiter = "__"


class SafetyNetSettings(BaseSettings):
    fastramqpi: FastRAMQPISettings = Field(
        default_factory=FastRAMQPISettings, description="FastRAMQPI settings"
    )

    safetynet_sftp: SafetyNetSFTP | None = None

    safetynet_adm_unit_uuid: UUID
    safetynet_med_unit_uuid: UUID | None = None

    source_system: SourceSystem = SourceSystem.OPUS

    include_manager_cpr: bool = False
    # Only include these SD engagement types (user keys)
    allowed_sd_engagement_types: list[str] = ["fuldtid", "månedsløn"]

    class Config:
        env_nested_delimiter = "__"
