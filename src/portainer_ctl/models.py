from enum import Enum
from typing import Dict, List, Optional


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


class DeploymentRequest:
    name: str
    compose: str
    configs: Dict[str, str]
    secrets: Dict[str, str]
    variables: Dict[str, str]
