from dataclasses import dataclass, field
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


@dataclass
class EndpointCreationRequest:
    name: str = ""
    type: EndpointCreationType = EndpointCreationType.LocalDocker
    url: Optional[str] = None
    tagIds: List[int] = field(default_factory=list)
    groupId: int = 0


@dataclass
class DeploymentRequest:
    name: str = ""
    compose: str = ""
    configs: Dict[str, str] = field(default_factory=dict)
    secrets: Dict[str, str] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)
