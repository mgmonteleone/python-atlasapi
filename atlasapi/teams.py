from typing import Optional, List


class TeamRoles:
    def __init__(self, team_id: str, roles: List[str]):
        """Contains a team_id and its associated atlas access roles.

        Args:
            team_id (str):
            roles (List[str]): A list of Atlas access roles.
        """
        self.team_id = team_id
        self.roles = roles


class Team:
    def __init__(self, name: str, id: str = None, usernames: Optional[List[str]] = None, org_id: Optional[str] = None,
                 links: Optional[list] = None):
        """

        Args:
            org_id (str):  The unique identifier for the organization you want to associate the team with.
            name (str): the name of the team
            id (str): The unique identifier for the team.
            links (Optional[list]): Links to team related resources
            usernames Optional[List[str]]:  Valid email addresses of users to add to the new team. Atlas checks whether the user's email belongs to the organization, so that Atlas can properly associate the users to the teams.
        """
        self.org_id = org_id
        self.usernames = usernames
        self.links: Optional[list] = links
        self.id: Optional[str] = id
        self.name: str = name

    @classmethod
    def for_create(cls, org_id: str, name: str, usernames: List[str]):
        """
        Creates a Team object in the format needed to create in the Atlas API
        Args:
            usernames (List[str]):  Valid email addresses of users to add to the new team. Atlas checks whether the user's email belongs to the organization, so that Atlas can properly associate the users to the teams.
            org_id (str):  The unique identifier for the organization you want to associate the team with.
            name (str): the name of the team


        Returns: None

        """
        return cls(name=name, org_id=org_id, usernames=usernames)

    @property
    def as_create_dict(self) -> dict:
        """
        A dictionary in the format the Atlas API expects for Teams
        Returns:

        """
        return dict(name=self.name, usernames=self.usernames)


class TeamRoles:
    def __init__(self, team_id: str, roles: List[str]):
        self.team_id = team_id
        self.roles = roles