from typing import List, Optional
from uuid import UUID

from ..types import CPRNumber
from .base_model import BaseModel


class GetParentManager(BaseModel):
    org_units: "GetParentManagerOrgUnits"


class GetParentManagerOrgUnits(BaseModel):
    objects: List["GetParentManagerOrgUnitsObjects"]


class GetParentManagerOrgUnitsObjects(BaseModel):
    current: Optional["GetParentManagerOrgUnitsObjectsCurrent"]


class GetParentManagerOrgUnitsObjectsCurrent(BaseModel):
    parent: Optional["GetParentManagerOrgUnitsObjectsCurrentParent"]


class GetParentManagerOrgUnitsObjectsCurrentParent(BaseModel):
    managers: List["GetParentManagerOrgUnitsObjectsCurrentParentManagers"]


class GetParentManagerOrgUnitsObjectsCurrentParentManagers(BaseModel):
    user_key: str
    person: Optional[List["GetParentManagerOrgUnitsObjectsCurrentParentManagersPerson"]]


class GetParentManagerOrgUnitsObjectsCurrentParentManagersPerson(BaseModel):
    cpr_number: Optional[CPRNumber]
    engagements: List[
        "GetParentManagerOrgUnitsObjectsCurrentParentManagersPersonEngagements"
    ]


class GetParentManagerOrgUnitsObjectsCurrentParentManagersPersonEngagements(BaseModel):
    user_key: str
    org_unit_uuid: UUID
    engagement_type: "GetParentManagerOrgUnitsObjectsCurrentParentManagersPersonEngagementsEngagementType"


class GetParentManagerOrgUnitsObjectsCurrentParentManagersPersonEngagementsEngagementType(
    BaseModel
):
    user_key: str


GetParentManager.update_forward_refs()
GetParentManagerOrgUnits.update_forward_refs()
GetParentManagerOrgUnitsObjects.update_forward_refs()
GetParentManagerOrgUnitsObjectsCurrent.update_forward_refs()
GetParentManagerOrgUnitsObjectsCurrentParent.update_forward_refs()
GetParentManagerOrgUnitsObjectsCurrentParentManagers.update_forward_refs()
GetParentManagerOrgUnitsObjectsCurrentParentManagersPerson.update_forward_refs()
GetParentManagerOrgUnitsObjectsCurrentParentManagersPersonEngagements.update_forward_refs()
GetParentManagerOrgUnitsObjectsCurrentParentManagersPersonEngagementsEngagementType.update_forward_refs()
