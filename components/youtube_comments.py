import os
import time
from dataclasses import dataclass
from typing import Generator, Optional, Set
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


@dataclass
class YouTubeComment:
    author: str
    message: str


class YouTubeComments:

    def __init__(
        self,
        video_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.video_id = video_id or os.getenv("YOUTUBE_VIDEO_ID", "")
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY", "")

        if not self.video_id:
            raise ValueError("YOUTUBE_VIDEO_ID が設定されていません。")
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY が設定されていません。")

        self.youtube = build("youtube", "v3", developerKey=self.api_key)
        self.live_chat_id = self._fetch_live_chat_id(self.video_id)
        self.next_page_token: Optional[str] = None
        self._seen_ids: Set[str] = set()
        self._alive = True

    def _fetch_live_chat_id(self, video_id: str) -> str:
        res = (
            self.youtube.videos()
            .list(part="liveStreamingDetails", id=video_id)
            .execute()
        )
        items = res.get("items", [])
        if not items:
            raise RuntimeError(f"動画が見つかりません: {video_id}")

        details = items[0].get("liveStreamingDetails", {})
        chat_id = details.get("activeLiveChatId")
        if not chat_id:
            raise RuntimeError("activeLiveChatId が取得できません。")
        return chat_id

    def stream(
        self, default_poll_interval: float = 3.0
    ) -> Generator[YouTubeComment, None, None]:
        is_first = True

        while self._alive:
            try:
                params = {
                    "liveChatId": self.live_chat_id,
                    "part": "snippet,authorDetails",
                    "maxResults": 200,
                }
                if self.next_page_token:
                    params["pageToken"] = self.next_page_token

                res = self.youtube.liveChatMessages().list(**params).execute()

                self.next_page_token = res.get("nextPageToken")
                polling_ms = res.get("pollingIntervalMillis")
                sleep_sec = polling_ms / 1000.0 if polling_ms else default_poll_interval

                items = res.get("items", [])
                for item in items:
                    message_id = item.get("id")
                    if not message_id or message_id in self._seen_ids:
                        continue
                    self._seen_ids.add(message_id)

                    if is_first:
                        continue

                    snippet = item.get("snippet", {})
                    if snippet.get("type") != "textMessageEvent":
                        continue

                    author = item.get("authorDetails", {}).get("displayName", "名無し")
                    message = snippet.get("displayMessage") or snippet.get(
                        "textMessageDetails", {}
                    ).get("messageText", "")
                    if not message:
                        continue

                    yield YouTubeComment(author=author, message=message)

                is_first = False
                time.sleep(sleep_sec)

            except HttpError as e:
                print(f"\033[31mYouTube API エラー: {e}\033[0m")
                time.sleep(default_poll_interval * 2)
            except Exception as e:
                print(f"\033[31mYouTubeコメント取得エラー: {e}\033[0m")
                time.sleep(default_poll_interval)

    def terminate(self) -> None:
        self._alive = False
