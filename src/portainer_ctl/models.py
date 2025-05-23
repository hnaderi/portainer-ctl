from enum import Enum


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
    url: str | None
    tagIds: list[int]
    groupId: int
