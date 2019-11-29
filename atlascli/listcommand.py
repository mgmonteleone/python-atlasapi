from enum import Enum
import pprint

class ListFormat(Enum):

    short = "short"
    full = "full"

    def __str__(self):
        return self.value

class Commands(Enum):

    List="List"

    def __str__(self):
        return self.value


class ListCommand:
    """
    Execute the list command
    """

    def __init__(self, format:ListFormat = ListFormat.short):
        self._format = format

    def list_one(self, resource):
        if self._format is ListFormat.short:
            print(resource["id"])
        else:
            pprint.pprint(resource)

    def list_all(self, iterator):
        counter = 0
        for counter, resource in enumerate(iterator):
            self.list_one(resource)
        return counter
