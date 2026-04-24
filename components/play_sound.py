import os
import sounddevice as sd
from typing import Any, Dict, List, cast
from dotenv import load_dotenv

load_dotenv()


class PlaySound:
    def __init__(self, output_device_name: str | None = None) -> None:
        if output_device_name is None:
            output_device_name = os.getenv("CABLE_DEVICE_NAME", "CABLE Input")
        self.output_device_id = self._search_output_device_id(output_device_name)

    def _search_output_device_id(
        self, output_device_name: str, output_device_host_api: int = 0
    ) -> int:
        devices = cast(List[Dict[str, Any]], sd.query_devices())
        output_device_id = None

        for device in devices:
            is_output_device_name = output_device_name in device["name"]
            is_output_device_host_api = device["hostapi"] == output_device_host_api
            if is_output_device_name and is_output_device_host_api:
                output_device_id = device["index"]
                break

        if output_device_id is None:
            raise RuntimeError(f"出力デバイスが見つかりません: {output_device_name}")

        return output_device_id

    def play_sound(self, data, rate) -> bool:
        sd.play(data, rate, device=self.output_device_id)
        sd.wait()
        return True
