from typing import Optional


class Organization:
    def __init__(self, name: str, is_deleted: bool = False, links: Optional[list] = None, id: Optional[str] = None):
        """A single atlas organization, the top organizational level with Atlas

        Args:
            name (str):
            is_deleted (bool):
            links (List[str]):
            id (str):
        """
        self.id = id
        self.links = links
        self.is_deleted = is_deleted
        self.name = name

    @classmethod
    def from_dict(cls, data_dict: dict):
        """Creates class from an Atlas returned dict.

        Args:
            data_dict (dict): As returned by the atlas api.

        Returns:

        """
        return cls(data_dict.get("name"), data_dict.get("isDeleted", False), data_dict.get("links", []),
                   data_dict.get("id", None))

