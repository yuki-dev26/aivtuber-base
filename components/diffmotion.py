from typing import Any, Dict, Optional

import requests

BASE_URL = "http://localhost:37264"

_available: Optional[bool] = None


def check_available() -> bool:
    global _available
    if _available is not None:
        return _available
    try:
        requests.get(f"{BASE_URL}/presets", timeout=1)
        _available = True
        print("\033[36mDiffmotion: 接続OK\033[0m")
    except Exception:
        _available = False
        print(
            "\033[33mDiffmotion が起動していません。表情連動をスキップします。\033[0m"
        )
    return _available


# プリセットを切り替える
def switch_preset(preset_name: str) -> bool:
    if not check_available():
        return False

    url = f"{BASE_URL}/preset/switch"
    payload: Dict[str, Any] = {"name": preset_name}

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()

        data = response.json()
        if data.get("success"):
            print(f"プリセット切り替え: {preset_name}")
            return True
        else:
            print(f"APIエラー: {data.get('message')}")
            return False

    except Exception as e:
        print(f"エラー: プリセット切り替えに失敗しました: {e}")
        return False


# プリセットを取得する
def get_presets() -> list[str]:
    if not check_available():
        return []

    url = f"{BASE_URL}/presets"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        presets = []
        if data.get("success") and "windows" in data:
            for window in data["windows"]:
                for preset in window.get("presets", []):
                    presets.append(preset["name"])

        return sorted(list[str](set[str](presets)))

    except Exception as e:
        print(f"エラー: プリセットの取得に失敗しました: {e}")
        return []
