
class ApplicationError(Exception):
    pass


class ManifestError(ApplicationError):
    pass


class ValidationError(ManifestError):
    pass


class HomeAssistantError(ApplicationError):

    def __init__(self):
        super().__init__("There was an error connecting to the Home Assistant instance")


class AuthenticationError(HomeAssistantError):

    def __init__(self):
        super().__init__("The provided authentication token was rejected")