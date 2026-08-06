from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class GetEngagement(BaseModel):
    engagements: "GetEngagementEngagements"


class GetEngagementEngagements(BaseModel):
    objects: List["GetEngagementEngagementsObjects"]


class GetEngagementEngagementsObjects(BaseModel):
    validities: List["GetEngagementEngagementsObjectsValidities"]
    current: Optional["GetEngagementEngagementsObjectsCurrent"]


class GetEngagementEngagementsObjectsValidities(BaseModel):
    validity: "GetEngagementEngagementsObjectsValiditiesValidity"


class GetEngagementEngagementsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetEngagementEngagementsObjectsCurrent(BaseModel):
    user_key: str
    person: List["GetEngagementEngagementsObjectsCurrentPerson"]
    job_function: "GetEngagementEngagementsObjectsCurrentJobFunction"
    managers: List["GetEngagementEngagementsObjectsCurrentManagers"]


class GetEngagementEngagementsObjectsCurrentPerson(BaseModel):
    cpr_number: Optional[CPRNumber]
    given_name: str
    surname: str
    addresses: List["GetEngagementEngagementsObjectsCurrentPersonAddresses"]


class GetEngagementEngagementsObjectsCurrentPersonAddresses(BaseModel):
    value: str


class GetEngagementEngagementsObjectsCurrentJobFunction(BaseModel):
    name: str


class GetEngagementEngagementsObjectsCurrentManagers(BaseModel):
    person: Optional[List["GetEngagementEngagementsObjectsCurrentManagersPerson"]]
    engagement_response: Optional[
        "GetEngagementEngagementsObjectsCurrentManagersEngagementResponse"
    ]


class GetEngagementEngagementsObjectsCurrentManagersPerson(BaseModel):
    cpr_number: Optional[CPRNumber]
    engagements: List["GetEngagementEngagementsObjectsCurrentManagersPersonEngagements"]


class GetEngagementEngagementsObjectsCurrentManagersPersonEngagements(BaseModel):
    user_key: str
    engagement_type: (
        "GetEngagementEngagementsObjectsCurrentManagersPersonEngagementsEngagementType"
    )


class GetEngagementEngagementsObjectsCurrentManagersPersonEngagementsEngagementType(
    BaseModel
):
    user_key: str


class GetEngagementEngagementsObjectsCurrentManagersEngagementResponse(BaseModel):
    uuid: UUID
    current: Optional[
        "GetEngagementEngagementsObjectsCurrentManagersEngagementResponseCurrent"
    ]


class GetEngagementEngagementsObjectsCurrentManagersEngagementResponseCurrent(
    BaseModel
):
    user_key: str


GetEngagement.update_forward_refs()
GetEngagementEngagements.update_forward_refs()
GetEngagementEngagementsObjects.update_forward_refs()
GetEngagementEngagementsObjectsValidities.update_forward_refs()
GetEngagementEngagementsObjectsValiditiesValidity.update_forward_refs()
GetEngagementEngagementsObjectsCurrent.update_forward_refs()
GetEngagementEngagementsObjectsCurrentPerson.update_forward_refs()
GetEngagementEngagementsObjectsCurrentPersonAddresses.update_forward_refs()
GetEngagementEngagementsObjectsCurrentJobFunction.update_forward_refs()
GetEngagementEngagementsObjectsCurrentManagers.update_forward_refs()
GetEngagementEngagementsObjectsCurrentManagersPerson.update_forward_refs()
GetEngagementEngagementsObjectsCurrentManagersPersonEngagements.update_forward_refs()
GetEngagementEngagementsObjectsCurrentManagersPersonEngagementsEngagementType.update_forward_refs()
GetEngagementEngagementsObjectsCurrentManagersEngagementResponse.update_forward_refs()
GetEngagementEngagementsObjectsCurrentManagersEngagementResponseCurrent.update_forward_refs()
