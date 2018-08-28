from typing import Optional, NewType, List
from datetime import datetime

OptionalInt = NewType('OptionalInt', Optional[int])
OptionalStr = NewType('OptionalStr', Optional[str])
OptionalDateTime = NewType('OptionalDateTime', Optional[datetime])
OptionalBool = NewType('OptionalBool', Optional[bool])
ListOfStr = NewType('ListofStr', List[str])
ListofDict = NewType('ListOfDict', List[str])
OptionalFloat = NewType('OptionalFloat', Optional[float])