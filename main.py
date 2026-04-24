import os
import re
import time
from typing import Optional, Tuple

from dotenv import load_dotenv

from components.aivisspeech import Aivis
from components.diffmotion import check_available as check_diffmotion
from components.diffmotion import switch_preset
from components.openai import OpenAI
from components.play_sound import PlaySound
from components.youtube_comments import YouTubeComments

load_dotenv()

EMOTION_TAG_PATTERN = re.compile(r"^\s*<<([^<>]+)>>\s*")


def split_emotion(response: str) -> Tuple[Optional[str], str]:
    match = EMOTION_TAG_PATTERN.match(response)
    if not match:
        return None, response.strip()
    emotion = match.group(1).strip()
    body = EMOTION_TAG_PATTERN.sub("", response, count=1).strip()
    return emotion, body


def main() -> None:
    video_id = os.getenv("YOUTUBE_VIDEO_ID", "")
    if not video_id:
        raise SystemExit("YOUTUBE_VIDEO_ID が未設定です。")

    comments = YouTubeComments(video_id=video_id)
    openai_client = OpenAI()
    aivis = Aivis()
    player = PlaySound()
    check_diffmotion()

    print("\033[36mAIVTuberを起動しました。YouTubeコメントを待機中...\033[0m")

    try:
        for comment in comments.stream(default_poll_interval=3.0):
            print(f"\033[33m[{comment.author}] {comment.message}\033[0m")

            question = f"{comment.author}さんからのコメント: {comment.message}"
            response = openai_client.create_chat(question)
            if not response:
                continue

            emotion, body = split_emotion(response)
            if emotion:
                print(f"\033[35m感情: {emotion}\033[0m")
                switch_preset(emotion)
            if not body:
                continue

            print(f"\033[32m応答: {body}\033[0m")

            data, rate = aivis.get_voice(body)
            player.play_sound(data, rate)

            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n\033[36m停止します。\033[0m")
    finally:
        comments.terminate()


if __name__ == "__main__":
    main()
