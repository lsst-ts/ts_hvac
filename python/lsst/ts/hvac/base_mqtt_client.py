# This file is part of ts_hvac.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["BaseMqttClient"]

import logging
from abc import ABC, abstractmethod
from collections import deque


class BaseMqttClient(ABC):
    """Client class to connect to the HVAC MQTT server.

    Parameters
    ----------
    host: `str`
        The hostname of the MQTT server.
    port: `int`
        The port of the MQTT service.
    """

    def __init__(self, log: logging.Logger) -> None:
        self.log = log.getChild(type(self).__name__)
        self.msgs: deque = deque()
        self.connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Connect the client to the MQTT server."""
        raise NotImplementedError()

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect the client from the MQTT server."""
        raise NotImplementedError()

    @abstractmethod
    async def publish_mqtt_message(
        self, topic: str, payload: str, qos: int = 1, timeout: float = 5.0
    ) -> bool:
        """Publishes the specified payload to the specified topic on the MQTT
        server.

        Parameters
        ----------
        topic: `str`
            The topic to publish to.
        payload: `str`
            The payload to publish.
        qos: `int`
            The MQTT QoS parameter to be used in sending the message:
             * 0 = at most once
             * 1 = at least once
             * 2 = exactly once
        timeout: `float`
            Time after which to return a failure, in seconds.

        Returns
        -------
        is_published: `bool`
            True if the message was published successfully.
        """
        raise NotImplementedError()
