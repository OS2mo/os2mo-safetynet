from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetMedUnit(BaseModel):
    org_units: "GetMedUnitOrgUnits"


class GetMedUnitOrgUnits(BaseModel):
    objects: List["GetMedUnitOrgUnitsObjects"]


class GetMedUnitOrgUnitsObjects(BaseModel):
    current: Optional["GetMedUnitOrgUnitsObjectsCurrent"]


class GetMedUnitOrgUnitsObjectsCurrent(BaseModel):
    name: str
    uuid: UUID
    associations: List["GetMedUnitOrgUnitsObjectsCurrentAssociations"]
    parent: Optional["GetMedUnitOrgUnitsObjectsCurrentParent"]
    children: List["GetMedUnitOrgUnitsObjectsCurrentChildren"]


class GetMedUnitOrgUnitsObjectsCurrentAssociations(BaseModel):
    uuid: UUID


class GetMedUnitOrgUnitsObjectsCurrentParent(BaseModel):
    uuid: UUID


class GetMedUnitOrgUnitsObjectsCurrentChildren(BaseModel):
    uuid: UUID


GetMedUnit.update_forward_refs()
GetMedUnitOrgUnits.update_forward_refs()
GetMedUnitOrgUnitsObjects.update_forward_refs()
GetMedUnitOrgUnitsObjectsCurrent.update_forward_refs()
GetMedUnitOrgUnitsObjectsCurrentAssociations.update_forward_refs()
GetMedUnitOrgUnitsObjectsCurrentParent.update_forward_refs()
GetMedUnitOrgUnitsObjectsCurrentChildren.update_forward_refs()
