from typing import Optional, List


class AtlasUser:
    def __init__(self, country: str, email_address: str, first_name: str, last_name: str, roles: Optional[List[dict]],
                 username: Optional[str], links: Optional[List[str]] = None, mobile_number: str = None,
                 password: str = None, team_ids: Optional[List[str]] = None, id: str = None):
        self.username: str = username
        self.team_ids: Optional[List[str]] = team_ids
        self.roles: Optional[List[dict]] = roles
        self.password: str = password
        self.mobile_number: str = mobile_number
        self.links: Optional[List[str]] = links
        self.last_name: str = last_name
        self.id: Optional[str] = id
        self.first_name: str = first_name
        self.email_address: str = email_address
        self.country: str = country

    @classmethod
    def from_dict(cls, data_dict: dict):
        country = data_dict.get("country", None)
        email_address = data_dict.get("emailAddress", None)
        first_name = data_dict.get("firstName", None)
        last_name = data_dict.get("lastName", None)
        roles = data_dict.get("roles", [])
        username = data_dict.get("username", None)
        links = data_dict.get("links", None)
        mobile_number = data_dict.get("mobileNumber", None)
        password = data_dict.get("password", None)
        team_ids = data_dict.get("teamIds", None)
        id = data_dict.get("id", None)
        return cls(
            country, email_address, first_name, last_name, roles, username, links, mobile_number, password, team_ids,
            id)
