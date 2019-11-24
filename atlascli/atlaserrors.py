
from requests.exceptions import HTTPError


class AtlasError(HTTPError):
    def __init__(self, *args, **kwargs):
        self._text = kwargs.pop("text", None)

        super().__init__(*args, **kwargs)

    @property
    def text(self):
        return self._text

class AtlasAuthenticationError(AtlasError):
    pass


class AtlasGetError(AtlasError):
    pass


class AtlasPostError(AtlasError):
    pass


class AtlasPatchError(AtlasError):
    pass


class AtlasDeleteError(AtlasError):
    pass


class AtlasEnvironmentError(ValueError):
    pass


class AtlasInitialisationError(ValueError):
    pass
