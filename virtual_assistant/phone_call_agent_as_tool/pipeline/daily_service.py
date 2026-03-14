import time
import aiohttp
from dataclasses import dataclass
from virtual_assistant.phone_call_agent_as_tool.config.settings import daily as cfg


@dataclass(frozen=True)
class RoomInfo:
    url: str
    sip_uri: str


"""
Daily.co API client.

Responsible for creating rooms (with SIP enabled) and assigning meeting tokens.
"""


class DailyService:
    _BASE = cfg.api_url
    _HEADERS = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }

    async def create_sip_room(self, room_name: str) -> RoomInfo:
        """
        Create a Daily room with SIP dial-in enabled.

        returns Daily URL + SIP URI
        """

        payload = {
            "name": room_name,
            "properties": {
                "exp": int(time.time()) + cfg.room_ttl_seconds,
                "sip": {"sip_mode": "dial-in", "display_name": "Caller"},
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self._BASE}/rooms", headers=self._HEADERS, json=payload
            ) as resp:
                data = await resp.json()
                if resp.status not in (200, 201):
                    raise RuntimeError(f"[DailyService] Room creation failed: {data}")

        sip_endpoint = data.get("config", {}).get("sip_uri", {}).get("endpoint", "")
        if not sip_endpoint:
            raise RuntimeError("Daily Room created but SIP URI is missing.")

        room = RoomInfo(url=data["url"], sip_uri=f"sip:{sip_endpoint}")
        print(f"Daily room ready ❧ url={room.url}  sip={room.sip_uri}")
        return room

    async def create_owner_token(self, room_name: str) -> str:
        """Assign an owner meeting token for the given room."""

        payload = {
            "properties": {
                "room_name": room_name,
                "is_owner": True,
                "exp": int(time.time()) + cfg.room_ttl_seconds,
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self._BASE}/meeting-tokens", headers=self._HEADERS, json=payload
            ) as resp:
                data = await resp.json()
                if resp.status not in (200, 201):
                    raise RuntimeError(f"Daily Token creation failed: {data}")

        print("Daily Token Successfully created")
        return data["token"]
