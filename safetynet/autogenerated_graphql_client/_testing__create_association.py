from uuid import UUID

from .base_model import BaseModel


class TestingCreateAssociation(BaseModel):
    association_create: "TestingCreateAssociationAssociationCreate"


class TestingCreateAssociationAssociationCreate(BaseModel):
    uuid: UUID


TestingCreateAssociation.update_forward_refs()
TestingCreateAssociationAssociationCreate.update_forward_refs()
