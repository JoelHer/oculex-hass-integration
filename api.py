import aiohttp

class EOESApi:
    def __init__(self, host, port, api_key=None):
        self.base = f"http://{host}:{port}"
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def get_streams(self):
        async with self.session.get(f"{self.base}/streams") as resp:
            resp.raise_for_status()
            data = await resp.json()
            return [{"id": s, "name": s} for s in data["streams"]]

    async def get_stream_info(self, stream_id):
        async with self.session.get(f"{self.base}/streams/{stream_id}") as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_status(self, stream_id):
        info = await self.get_stream_info(stream_id)
        return info.get("status", "UNKNOWN")

    async def get_ocr(self, stream_id):
        """Fetch the OCR JSON for a stream (/streams/{id}/ocr)."""
        async with self.session.get(f"{self.base}/streams/{stream_id}/ocr") as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_image(self, stream_id):
        # keep your existing image endpoint, assumed to return raw image bytes
        async with self.session.get(f"{self.base}/streams/{stream_id}/ocr-withimage") as resp:
            resp.raise_for_status()
            return await resp.read()

    async def close(self):
        await self.session.close()
