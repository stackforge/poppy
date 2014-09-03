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

import abc

import six

from poppy.manager.base import providers as mproviders

@six.add_metaclass(abc.ABCMeta)
class ManagerDriverBase(object):
    def __init__(self, conf, storage, providers):
        self._conf = conf
        self._storage = storage
        self._providers = providers
        self.provider_wrapper = mproviders.ProviderWrapper()

    @property
    def storage(self):
        return self._storage

    @property
    def providers(self):
        return self._providers

    @abc.abstractproperty
    def services_controller(self):
        """Returns the driver's services controller."""
        raise NotImplementedError

    @abc.abstractmethod
    def health(self):
        """Returns the health of storage and providers."""
        raise NotImplementedError
