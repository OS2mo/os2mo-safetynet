from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from ..types import CPRNumber
from ._testing__create_association import (
    TestingCreateAssociation,
    TestingCreateAssociationAssociationCreate,
)
from ._testing__create_class import TestingCreateClass, TestingCreateClassClassCreate
from ._testing__create_employee import (
    TestingCreateEmployee,
    TestingCreateEmployeeEmployeeCreate,
)
from ._testing__create_engagement import (
    TestingCreateEngagement,
    TestingCreateEngagementEngagementCreate,
)
from ._testing__create_facet import TestingCreateFacet, TestingCreateFacetFacetCreate
from ._testing__create_manager import (
    TestingCreateManager,
    TestingCreateManagerManagerCreate,
)
from ._testing__create_org import TestingCreateOrg, TestingCreateOrgOrgCreate
from ._testing__create_org_unit import (
    TestingCreateOrgUnit,
    TestingCreateOrgUnitOrgUnitCreate,
)
from .async_base_client import AsyncBaseClient
from .base_model import UNSET, UnsetType
from .get_adm_unit import GetAdmUnit, GetAdmUnitOrgUnits
from .get_association import GetAssociation, GetAssociationAssociations
from .get_engagement import GetEngagement, GetEngagementEngagements
from .get_med_unit import GetMedUnit, GetMedUnitOrgUnits
from .get_parent_manager import GetParentManager, GetParentManagerOrgUnits


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):

    async def get_adm_unit(
        self, org_unit: Union[Optional[List[UUID]], UnsetType] = UNSET
    ) -> GetAdmUnitOrgUnits:
        query = gql("""
            query GetAdmUnit($org_unit: [UUID!]) {
              org_units(filter: {uuids: $org_unit}) {
                objects {
                  current {
                    name
                    uuid
                    engagements {
                      uuid
                    }
                    parent {
                      uuid
                    }
                    children {
                      uuid
                    }
                    managers(inherit: true) {
                      user_key
                      person {
                        cpr_number
                        engagements {
                          user_key
                          org_unit_uuid
                          engagement_type {
                            user_key
                          }
                        }
                      }
                      engagement_response {
                        uuid
                        current {
                          user_key
                        }
                      }
                    }
                    addresses(filter: {address_type_user_keys: "Pnummer"}) {
                      value
                    }
                    related_units {
                      org_units {
                        uuid
                      }
                    }
                    ancestors {
                      uuid
                    }
                  }
                }
              }
            }
            """)
        variables: dict[str, object] = {"org_unit": org_unit}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetAdmUnit.parse_obj(data).org_units

    async def get_engagement(
        self, uuid: Union[Optional[List[UUID]], UnsetType] = UNSET
    ) -> GetEngagementEngagements:
        query = gql("""
            query GetEngagement($uuid: [UUID!]) {
              engagements(filter: {uuids: $uuid, from_date: null, to_date: null}) {
                objects {
                  validities {
                    validity {
                      from
                      to
                    }
                  }
                  current {
                    user_key
                    person {
                      cpr_number
                      given_name
                      surname
                      addresses(filter: {address_type_user_keys: "AD-Email"}) {
                        value
                      }
                    }
                    job_function {
                      name
                    }
                    managers(exclude_self: true, inherit: true) {
                      person {
                        cpr_number
                        engagements {
                          user_key
                          engagement_type {
                            user_key
                          }
                        }
                      }
                      engagement_response {
                        uuid
                        current {
                          user_key
                        }
                      }
                    }
                  }
                }
              }
            }
            """)
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetEngagement.parse_obj(data).engagements

    async def get_med_unit(
        self, org_unit: Union[Optional[List[UUID]], UnsetType] = UNSET
    ) -> GetMedUnitOrgUnits:
        query = gql("""
            query GetMedUnit($org_unit: [UUID!]) {
              org_units(filter: {uuids: $org_unit}) {
                objects {
                  current {
                    name
                    uuid
                    associations {
                      uuid
                    }
                    parent {
                      uuid
                    }
                    children {
                      uuid
                    }
                  }
                }
              }
            }
            """)
        variables: dict[str, object] = {"org_unit": org_unit}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetMedUnit.parse_obj(data).org_units

    async def get_association(
        self, uuid: Union[Optional[List[UUID]], UnsetType] = UNSET
    ) -> GetAssociationAssociations:
        query = gql("""
            query GetAssociation($uuid: [UUID!]) {
              associations(filter: {uuids: $uuid, from_date: null, to_date: null}) {
                objects {
                  validities {
                    validity {
                      from
                      to
                    }
                  }
                  current {
                    association_type {
                      name
                      user_key
                      uuid
                    }
                    dynamic_class {
                      full_name
                      name
                      user_key
                      uuid
                    }
                    person {
                      cpr_number
                    }
                  }
                }
              }
            }
            """)
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetAssociation.parse_obj(data).associations

    async def get_parent_manager(
        self, org_unit: Union[Optional[List[UUID]], UnsetType] = UNSET
    ) -> GetParentManagerOrgUnits:
        query = gql("""
            query GetParentManager($org_unit: [UUID!]) {
              org_units(filter: {uuids: $org_unit}) {
                objects {
                  current {
                    parent {
                      managers(inherit: true) {
                        user_key
                        person {
                          cpr_number
                          engagements {
                            user_key
                            org_unit_uuid
                            engagement_type {
                              user_key
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
            """)
        variables: dict[str, object] = {"org_unit": org_unit}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return GetParentManager.parse_obj(data).org_units

    async def _testing__create_org(self) -> TestingCreateOrgOrgCreate:
        query = gql("""
            mutation _Testing_CreateOrg {
              org_create(input: {municipality_code: null}) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrg.parse_obj(data).org_create

    async def _testing__create_facet(
        self, user_key: str, from_date: datetime
    ) -> TestingCreateFacetFacetCreate:
        query = gql("""
            mutation _Testing_CreateFacet($user_key: String!, $from_date: DateTime!) {
              facet_create(input: {user_key: $user_key, validity: {from: $from_date}}) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {"user_key": user_key, "from_date": from_date}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateFacet.parse_obj(data).facet_create

    async def _testing__create_class(
        self, user_key: str, name: str, facet_uuid: UUID, from_date: datetime
    ) -> TestingCreateClassClassCreate:
        query = gql("""
            mutation _Testing_CreateClass($user_key: String!, $name: String!, $facet_uuid: UUID!, $from_date: DateTime!) {
              class_create(
                input: {user_key: $user_key, name: $name, facet_uuid: $facet_uuid, validity: {from: $from_date}}
              ) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {
            "user_key": user_key,
            "name": name,
            "facet_uuid": facet_uuid,
            "from_date": from_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateClass.parse_obj(data).class_create

    async def _testing__create_employee(
        self, given_name: str, surname: str, cpr_number: CPRNumber
    ) -> TestingCreateEmployeeEmployeeCreate:
        query = gql("""
            mutation _Testing_CreateEmployee($given_name: String!, $surname: String!, $cpr_number: CPR!) {
              employee_create(
                input: {given_name: $given_name, surname: $surname, cpr_number: $cpr_number}
              ) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {
            "given_name": given_name,
            "surname": surname,
            "cpr_number": cpr_number,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEmployee.parse_obj(data).employee_create

    async def _testing__create_org_unit(
        self,
        name: str,
        user_key: str,
        org_unit_type: UUID,
        from_date: datetime,
        parent: Union[Optional[UUID], UnsetType] = UNSET,
    ) -> TestingCreateOrgUnitOrgUnitCreate:
        query = gql("""
            mutation _Testing_CreateOrgUnit($name: String!, $user_key: String!, $org_unit_type: UUID!, $from_date: DateTime!, $parent: UUID) {
              org_unit_create(
                input: {name: $name, user_key: $user_key, org_unit_type: $org_unit_type, parent: $parent, validity: {from: $from_date}}
              ) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {
            "name": name,
            "user_key": user_key,
            "org_unit_type": org_unit_type,
            "from_date": from_date,
            "parent": parent,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateOrgUnit.parse_obj(data).org_unit_create

    async def _testing__create_engagement(
        self,
        user_key: str,
        person: UUID,
        org_unit: UUID,
        engagement_type: UUID,
        job_function: UUID,
        from_date: datetime,
    ) -> TestingCreateEngagementEngagementCreate:
        query = gql("""
            mutation _Testing_CreateEngagement($user_key: String!, $person: UUID!, $org_unit: UUID!, $engagement_type: UUID!, $job_function: UUID!, $from_date: DateTime!) {
              engagement_create(
                input: {user_key: $user_key, person: $person, org_unit: $org_unit, engagement_type: $engagement_type, job_function: $job_function, validity: {from: $from_date}}
              ) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {
            "user_key": user_key,
            "person": person,
            "org_unit": org_unit,
            "engagement_type": engagement_type,
            "job_function": job_function,
            "from_date": from_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateEngagement.parse_obj(data).engagement_create

    async def _testing__create_manager(
        self,
        user_key: str,
        person: UUID,
        org_unit: UUID,
        manager_type: UUID,
        manager_level: UUID,
        responsibility: List[UUID],
        from_date: datetime,
        engagement: Union[Optional[UUID], UnsetType] = UNSET,
    ) -> TestingCreateManagerManagerCreate:
        query = gql("""
            mutation _Testing_CreateManager($user_key: String!, $person: UUID!, $org_unit: UUID!, $manager_type: UUID!, $manager_level: UUID!, $responsibility: [UUID!]!, $from_date: DateTime!, $engagement: UUID) {
              manager_create(
                input: {user_key: $user_key, person: $person, org_unit: $org_unit, manager_type: $manager_type, manager_level: $manager_level, responsibility: $responsibility, engagement: $engagement, validity: {from: $from_date}}
              ) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {
            "user_key": user_key,
            "person": person,
            "org_unit": org_unit,
            "manager_type": manager_type,
            "manager_level": manager_level,
            "responsibility": responsibility,
            "from_date": from_date,
            "engagement": engagement,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateManager.parse_obj(data).manager_create

    async def _testing__create_association(
        self,
        user_key: str,
        person: UUID,
        org_unit: UUID,
        association_type: UUID,
        from_date: datetime,
        trade_union: Union[Optional[UUID], UnsetType] = UNSET,
    ) -> TestingCreateAssociationAssociationCreate:
        query = gql("""
            mutation _Testing_CreateAssociation($user_key: String!, $person: UUID!, $org_unit: UUID!, $association_type: UUID!, $from_date: DateTime!, $trade_union: UUID) {
              association_create(
                input: {user_key: $user_key, person: $person, org_unit: $org_unit, association_type: $association_type, trade_union: $trade_union, validity: {from: $from_date}}
              ) {
                uuid
              }
            }
            """)
        variables: dict[str, object] = {
            "user_key": user_key,
            "person": person,
            "org_unit": org_unit,
            "association_type": association_type,
            "from_date": from_date,
            "trade_union": trade_union,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingCreateAssociation.parse_obj(data).association_create
