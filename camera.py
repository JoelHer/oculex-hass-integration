from homeassistant.components.camera import Camera
from .const import DOMAIN
import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    streams = await api.get_streams()
    async_add_entities(EOESCamera(api, s["id"]) for s in streams)

class EOESCamera(Camera):
    def __init__(self, api, stream_id):
        super().__init__()
        self.api = api
        self.stream_id = stream_id
        self._attr_name = f"Oculex {stream_id} Camera"

    async def async_camera_image(self, width=None, height=None):
        return await self.api.get_image(self.stream_id)
