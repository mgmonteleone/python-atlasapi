from enum import Enum
from isodate import isodatetime
from datetime import datetime
from typing import Optional


class Project:
    def __init__(self, name: str, org_id: str, created_date: Optional[datetime] = None,
                 cluster_count: Optional[int] = None, id: Optional[str] = None, links: list = None,
                 with_default_alert_settings: Optional[bool] = True,
                 project_owner_id: str = None) -> None:
        """
        A single Atlas Project/Group

        Groups and projects are synonymous terms. Your {GROUP-ID} is the same as your project ID. For existing groups,
         your group/project ID remains the same. The resource and corresponding endpoints use the term groups.
        Args:
            id (str): The unique identifier of the project. You can use this value for populating the {GROUP-ID}
            parameter of other Atlas Administration API endpoints.
            name (str): The name of the project. You can use this value for populating the {GROUP-NAME} parameter of the /groups/byName/{GROUP-NAME} endpoint.
            links (list): One or more uniform resource locators that link to sub-resources and/or related resources. The Web Linking Specification explains the relation-types between URLs.
            org_id (str): The unique identifier of the Atlas organization to which the project belongs.
            created_date (Optional[datetime]): The ISO-8601-formatted timestamp of when Atlas created the project.
            cluster_count (int): The number of Atlas clusters deployed in the project.
            with_default_alert_settings (bool): Flag that indicates whether to create the new project with the default alert settings enabled. This parameter defaults to true.
        """
        self.project_owner_id: Optional[str] = project_owner_id
        self.with_default_alert_settings: bool = with_default_alert_settings
        self.cluster_count: Optional[int] = cluster_count
        self.created_date: Optional[datetime] = created_date
        self.org_id: str = org_id
        self.links: Optional[list] = links
        self.name: str = name
        self.id: Optional[str] = id

    @classmethod
    def for_create(cls, name: str, org_id: str, with_default_alert_settings: bool = True, project_owner_id: str = None):
        """
        Creates a new Project object for use in creating a new project.

        Only name and org_id are required.
        Args:
            project_owner_id (str): 	Unique 24-hexadecimal digit string that identifies the Atlas user account to be granted the Project Owner role on the specified project. If you set this parameter, it overrides the default value of the oldest Organization Owner.
            name (str): The name of the project. You can use this value for populating the {GROUP-NAME} parameter of the /groups/byName/{GROUP-NAME} endpoint.
            org_id (str): The unique identifier of the Atlas organization to which the project belongs.
            with_default_alert_settings (bool): Flag that indicates whether to create the new project with the default alert settings enabled. This parameter defaults to true.

        Returns:

        """
        return cls(name=name, org_id=org_id, with_default_alert_settings=with_default_alert_settings,
                   project_owner_id=project_owner_id)

    @classmethod
    def from_dict(cls, data_dict):
        """
        Creates a Project object from a passed dict, in the format of the Atlas API.
        Args:
            data_dict (dict): A dictionary in the format of the Atlas API.

        Returns:

        """
        return cls(id=data_dict.get("id"), name=data_dict.get("name"),
                   links=data_dict.get("links", []), org_id=data_dict.get("orgId"),
                   created_date=data_dict.get("created"), cluster_count=data_dict.get("clusterCount"))

    @property
    def create_dict(self) -> dict:
        """
        A dictionary in the format Atlas API "create project expects"

        Returns: A dictionary in the format Atlas API "create project expects"

        """
        return dict(name=self.name, orgId = self.org_id, withDefaultAlertsSettings=self.with_default_alert_settings)

"""
test_dict = {
    "clusterCount": 2,
    "created": "2016-07-14T14:19:33Z",
    "id": "5a0a1e7e0f2912c554080ae6",
    "links": [],
    "name": "DocsFeedbackGroup",
    "orgId": "5a0a1e7e0f2912c554080adc"
}

print(Project.for_create(org_id='34', name='test_project').as_create_dict)
"""