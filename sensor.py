from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = []
    for stream_id in coordinator.data.keys():
        entities.append(EOESSensor(coordinator, stream_id, "ocr"))
        entities.append(EOESSensor(coordinator, stream_id, "status"))

    async_add_entities(entities)


class EOESSensor(SensorEntity):
    def __init__(self, coordinator, stream_id, type_):
        self.coordinator = coordinator
        self.stream_id = stream_id
        self.type_ = type_
        self._attr_name = f"Oculex {stream_id} {type_}"
        self._attr_unique_id = f"oculex_{stream_id}_{type_}"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self.stream_id, {})
        if self.type_ == "ocr":
            ocr_data = data.get("ocr", {}).get("results", {}).get("aggregate", {})
            value = ocr_data.get("value")
            # try to return a number (Home Assistant likes numeric native_value for numeric sensors)
            try:
                return float(value) if value is not None else None
            except (ValueError, TypeError):
                return None
        return data.get(self.type_)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.stream_id, {})
        if self.type_ == "ocr":
            ocr_data = data.get("ocr", {}).get("results", {}).get("aggregate", {})
            # normalize keys (avoid hyphens in attr names)
            return {
                "confidence": ocr_data.get("confidence"),
                "timestamp": ocr_data.get("timestamp"),
                "image_fingerprint": ocr_data.get("image-fingerprint") or ocr_data.get("image_fingerprint"),
            }
        return None

    async def async_update(self):
        # trigger coordinator refresh (coordinator caches and coordinates polling)
        await self.coordinator.async_request_refresh()