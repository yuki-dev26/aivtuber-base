import io
import json
import os
import numpy as np
import requests
import soundfile
from typing import Optional, Tuple
from dotenv import load_dotenv

load_dotenv()


class Aivis:
    def __init__(
        self,
        speaker_id: Optional[int] = None,
        speed_scale: Optional[float] = None,
        intonation_scale: Optional[float] = None,
    ) -> None:
        self.url = "http://127.0.0.1:10101"

        self.speaker_id = (
            speaker_id if speaker_id is not None else int(os.getenv("SPEAKER_ID", "0"))
        )
        self.speed_scale = (
            speed_scale
            if speed_scale is not None
            else float(os.getenv("SPEED_SCALE", "1.0"))
        )
        self.intonation_scale = (
            intonation_scale
            if intonation_scale is not None
            else float(os.getenv("INTONATION_SCALE", "1.0"))
        )

        self.session = requests.Session()
        self.session.headers.update(
            {"accept": "audio/wav", "Content-Type": "application/json"}
        )

    def get_voice(self, text: str) -> Tuple[np.ndarray, int]:
        query = self.session.post(
            f"{self.url}/audio_query",
            params={"text": text, "speaker": self.speaker_id},
        ).json()
        query["speedScale"] = self.speed_scale
        query["intonationScale"] = self.intonation_scale

        res = self.session.post(
            f"{self.url}/synthesis",
            params={"speaker": self.speaker_id},
            data=json.dumps(query),
        )
        return soundfile.read(io.BytesIO(res.content))
