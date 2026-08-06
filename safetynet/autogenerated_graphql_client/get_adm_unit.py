from typing import List, Optional
from uuid import UUID

from ..types import CPRNumber
from .base_model import BaseModel


class GetAdmUnit(BaseModel):
    org_units: "GetAdmUnitOrgUnits"


class GetAdmUnitOrgUnits(BaseModel):
    objects: List["GetAdmUnitOrgUnitsObjects"]


class GetAdmUnitOrgUnitsObjects(BaseModel):
    current: Optional["GetAdmUnitOrgUnitsObjectsCurrent"]


class GetAdmUnitOrgUnitsObjectsCurrent(BaseModel):
    name: str
    uuid: UUID
    engagements: List["GetAdmUnitOrgUnitsObjectsCurrentEngagements"]
    parent: Optional["GetAdmUnitOrgUnitsObjectsCurrentParent"]
    children: List["GetAdmUnitOrgUnitsObjectsCurrentChildren"]
    managers: List["GetAdmUnitOrgUnitsObjectsCurrentManagers"]
    addresses: List["GetAdmUnitOrgUnitsObjectsCurrentAddresses"]
    related_units: List["GetAdmUnitOrgUnitsObjectsCurrentRelatedUnits"]
    ancestors: List["GetAdmUnitOrgUnitsObjectsCurrentAncestors"]


class GetAdmUnitOrgUnitsObjectsCurrentEngagements(BaseModel):
    uuid: UUID


class GetAdmUnitOrgUnitsObjectsCurrentParent(BaseModel):
    uuid: UUID


class GetAdmUnitOrgUnitsObjectsCurrentChildren(BaseModel):
    uuid: UUID


class GetAdmUnitOrgUnitsObjectsCurrentManagers(BaseModel):
    user_key: str
    person: Optional[List["GetAdmUnitOrgUnitsObjectsCurrentManagersPerson"]]
    engagement_response: Optional[
        "GetAdmUnitOrgUnitsObjectsCurrentManagersEngagementResponse"
    ]


class GetAdmUnitOrgUnitsObjectsCurrentManagersPerson(BaseModel):
    cpr_number: Optional[CPRNumber]
    engagements: List["GetAdmUnitOrgUnitsObjectsCurrentManagersPersonEngagements"]


class GetAdmUnitOrgUnitsObjectsCurrentManagersPersonEngagements(BaseModel):
    user_key: str
    org_unit_uuid: UUID
    engagement_type: (
        "GetAdmUnitOrgUnitsObjectsCurrentManagersPersonEngagementsEngagementType"
    )


class GetAdmUnitOrgUnitsObjectsCurrentManagersPersonEngagementsEngagementType(
    BaseModel
):
    user_key: str


class GetAdmUnitOrgUnitsObjectsCurrentManagersEngagementResponse(BaseModel):
    uuid: UUID
    current: Optional[
        "GetAdmUnitOrgUnitsObjectsCurrentManagersEngagementResponseCurrent"
    ]


class GetAdmUnitOrgUnitsObjectsCurrentManagersEngagementResponseCurrent(BaseModel):
    user_key: str


class GetAdmUnitOrgUnitsObjectsCurrentAddresses(BaseModel):
    value: str


class GetAdmUnitOrgUnitsObjectsCurrentRelatedUnits(BaseModel):
    org_units: List["GetAdmUnitOrgUnitsObjectsCurrentRelatedUnitsOrgUnits"]


class GetAdmUnitOrgUnitsObjectsCurrentRelatedUnitsOrgUnits(BaseModel):
    uuid: UUID


class GetAdmUnitOrgUnitsObjectsCurrentAncestors(BaseModel):
    uuid: UUID


GetAdmUnit.update_forward_refs()
GetAdmUnitOrgUnits.update_forward_refs()
GetAdmUnitOrgUnitsObjects.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrent.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentEngagements.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentParent.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentChildren.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentManagers.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentManagersPerson.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentManagersPersonEngagements.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentManagersPersonEngagementsEngagementType.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentManagersEngagementResponse.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentManagersEngagementResponseCurrent.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentAddresses.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentRelatedUnits.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentRelatedUnitsOrgUnits.update_forward_refs()
GetAdmUnitOrgUnitsObjectsCurrentAncestors.update_forward_refs()
