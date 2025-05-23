from enum import Enum
from typing import List, Optional


class EndpointCreationType(Enum):
    LocalDocker = 1
    Agent = 2

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return EndpointCreationType[s]
        except KeyError:
            raise ValueError()


class EndpointCreationRequest:
    name: str
    type: EndpointCreationType
    url: Optional[str]
    tagIds: List[int]
    groupId: int
