# Copyright (c) 2019 Joe Drumgoole
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
