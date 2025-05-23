class EndpointCreationType:
    LocalDocker = 1
    Agent = 2


class EndpointCreationRequest:
    name: str
    type: EndpointCreationType
    url: str | None
    tagIds: list[int]
    groupId: int
