# Copyright (c) 2014 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Default manager driver implementation."""

from poppy.common import decorators
from poppy.manager import base
from poppy.manager.default import controllers


class DefaultManagerDriver(base.Driver):

    def __init__(self, conf, storage, providers):
        super(DefaultManagerDriver, self).__init__(conf, storage, providers)

    @decorators.lazy_property(write=False)
    def services_controller(self):
        return controllers.Services(self)

    @decorators.lazy_property(write=False)
    def home_controller(self):
        return controllers.Home(self)

    @decorators.lazy_property(write=False)
    def flavors_controller(self):
        return controllers.Flavors(self)

    def health_provider(self, provider):
        """Returns the health of provider."""

        return (provider, self.providers[provider].obj.is_alive())

    def health_storage(self):
        """Returns the health of storage."""

        return (self.storage.storage_name, self.storage.is_alive())

    def health_providers(self):
        """Returns the health of storage and providers."""

        health_providers = self.providers.map(self.provider_wrapper.health)

        return health_providers
