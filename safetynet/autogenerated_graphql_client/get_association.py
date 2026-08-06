from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import BaseModel


class GetAssociation(BaseModel):
    associations: "GetAssociationAssociations"


class GetAssociationAssociations(BaseModel):
    objects: List["GetAssociationAssociationsObjects"]


class GetAssociationAssociationsObjects(BaseModel):
    validities: List["GetAssociationAssociationsObjectsValidities"]
    current: Optional["GetAssociationAssociationsObjectsCurrent"]


class GetAssociationAssociationsObjectsValidities(BaseModel):
    validity: "GetAssociationAssociationsObjectsValiditiesValidity"


class GetAssociationAssociationsObjectsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetAssociationAssociationsObjectsCurrent(BaseModel):
    association_type: Optional[
        "GetAssociationAssociationsObjectsCurrentAssociationType"
    ]
    dynamic_class: Optional["GetAssociationAssociationsObjectsCurrentDynamicClass"]
    person: List["GetAssociationAssociationsObjectsCurrentPerson"]


class GetAssociationAssociationsObjectsCurrentAssociationType(BaseModel):
    name: str
    user_key: str
    uuid: UUID


class GetAssociationAssociationsObjectsCurrentDynamicClass(BaseModel):
    full_name: str
    name: str
    user_key: str
    uuid: UUID


class GetAssociationAssociationsObjectsCurrentPerson(BaseModel):
    cpr_number: Optional[CPRNumber]


GetAssociation.update_forward_refs()
GetAssociationAssociations.update_forward_refs()
GetAssociationAssociationsObjects.update_forward_refs()
GetAssociationAssociationsObjectsValidities.update_forward_refs()
GetAssociationAssociationsObjectsValiditiesValidity.update_forward_refs()
GetAssociationAssociationsObjectsCurrent.update_forward_refs()
GetAssociationAssociationsObjectsCurrentAssociationType.update_forward_refs()
GetAssociationAssociationsObjectsCurrentDynamicClass.update_forward_refs()
GetAssociationAssociationsObjectsCurrentPerson.update_forward_refs()
