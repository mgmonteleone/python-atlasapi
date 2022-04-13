from typing import Optional


class Organization:
    def __init__(self, name: str, is_deleted: bool = False, links: Optional[list] = None, id: Optional[str] = None):
        self.id = id
        self.links = links
        self.is_deleted = is_deleted
        self.name = name

    @classmethod
    def from_dict(cls, data_dict: dict):
        return cls(data_dict.get("name"), data_dict.get("isDeleted", False), data_dict.get("links", []),
                   data_dict.get("id", None))
