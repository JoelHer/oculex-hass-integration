from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
from .const import DOMAIN
from .api import EOESApi
import logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    api = EOESApi(entry.data["host"], entry.data["port"], entry.data.get("api_key"))

    async def async_update_data():
        streams = await api.get_streams()
        results = {}
        for stream in streams:
            sid = stream["id"]
            # status
            try:
                status = await api.get_status(sid)
            except Exception:  # keep broad to avoid coordinator crash
                _LOGGER.exception("Failed to fetch status for %s", sid)
                status = "UNKNOWN"

            # ocr
            try:
                ocr = await api.get_ocr(sid)
            except Exception:
                _LOGGER.exception("Failed to fetch OCR for %s", sid)
                ocr = {}  # keep empty so sensors don't break

            results[sid] = {"status": status, "ocr": ocr}
        return results

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Oculex data",
        update_method=async_update_data,
        update_interval=timedelta(seconds=10),
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "camera"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "camera"])
    if unload_ok:
        api = hass.data[DOMAIN][entry.entry_id]["api"]
        # close the aiohttp session
        try:
            await api.close()
        except Exception:
            _LOGGER.exception("Error closing EOESApi session")
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok