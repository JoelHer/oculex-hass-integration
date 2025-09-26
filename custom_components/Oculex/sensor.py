from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities = []
    for stream_id in coordinator.data.keys():
        entities.append(EOESSensor(coordinator, stream_id, "ocr", "measurement"))
        entities.append(EOESSensor(coordinator, stream_id, "status"))

    async_add_entities(entities)


class EOESSensor(SensorEntity):
    def __init__(self, coordinator, stream_id, type_, device_class="measurement"):
        self.coordinator = coordinator
        self.stream_id = stream_id
        self.type_ = type_
        self._attr_device_class = device_class
        self._attr_name = f"Oculex {stream_id} {type_}"
        self._attr_unique_id = f"oculex_{stream_id}_{type_}"

    @property
    def native_value(self):
        data = self.coordinator.data.get(self.stream_id, {})
        if self.type_ == "ocr":
            ocr_data = data.get("ocr", {})
            results = ocr_data.get("results", [])

            if not results:
                return None

            # join texts
            text_value = "".join(r.get("text", "") for r in results)
            if not text_value:
                return None

            # try converting to float
            try:
                return float(text_value)
            except ValueError:
                return None

        return data.get(self.type_)

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(self.stream_id, {})
        if self.type_ == "ocr":
            ocr_data = data.get("ocr", {})
            results = ocr_data.get("results", [])

            if not results:
                return None

            # average confidence
            confidences = [r.get("confidence") for r in results if r.get("confidence") is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else None

            return {
                "confidence": avg_confidence,
                "timestamp": ocr_data.get("timestamp"),
                "cached": ocr_data.get("cached"),
            }
        return None

    async def async_update(self):
        # trigger coordinator refresh
        await self.coordinator.async_request_refresh()
