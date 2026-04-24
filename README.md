# aivtuber-base

<img src="https://skillicons.dev/icons?i=py&perline=8" />

YouTube Live のコメントを拾って OpenAI で応答を生成し、AivisSpeech で音声合成して出力する、AIVTuberシステムの最小構成。
本システムをベースに機能追加や改修などの独自カスタマイズを推奨します。

## 構成

```text
aivtuber-base/
├── main.py                  # システム
├── pyproject.toml / uv.lock
├── .env.example
├── config/
│   └── character.md         # キャラクター設定（感情タグ定義込み）
└── components/
    ├── youtube_comments.py  # YouTube Data API v3 でライブチャット取得
    ├── openai.py            # OpenAI Responses API
    ├── aivisspeech.py       # AivisSpeechで合成音声
    ├── play_sound.py        # 出力デバイス再生
    └── diffmotion.py        # Diffmotion プリセット切替
```

## 処理フロー

1. `YouTubeComments.stream()` でライブチャットを取得
2. `OpenAI.create_chat()` に投げて応答を生成（`config/character.md` がシステムプロンプト）
3. 応答に含まれる `<<感情名>>` タグを抽出 → `diffmotion.switch_preset()` でモデル表情を切替
4. 本文を `Aivis.get_voice()` で音声合成 → `PlaySound.play_sound()` で再生

## 必要なもの

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [AivisSpeech Engine](https://aivis-project.com/) をローカル起動（`http://127.0.0.1:10101`）
- OpenAI API キー：<https://note.com/yuki_tech/n/nbc29be8da07f/>
- YouTube Data API v3 API キー：<https://note.com/yuki_tech/n/na82ad826df1f/>
- 配信中の YouTube Live ID（URL の `v=` 以降）
- 出力デバイス（VB-CABLE など仮想オーディオデバイス推奨）
- 任意: [Diffmotion](https://diffmotion.app/) がローカル起動（`http://localhost:37264`）していると感情連動プリセット切替が動く

## セットアップ

```bash
uv sync
```

`.env` を作って各値を埋める:

```env
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-5.4-mini"

YOUTUBE_API_KEY="AIza..."
YOUTUBE_VIDEO_ID="xxxxxxxxxxx"

SPEAKER_ID="888753760"
SPEED_SCALE="1.0"
INTONATION_SCALE="1.0"

CABLE_DEVICE_NAME="CABLE Input"
```

## 起動

AivisSpeech Engine を起動した上で:

```bash
uv run python main.py
```

停止は `Ctrl + C`。

## キャラクター / 感情タグのカスタマイズ

`config/character.md` がそのままシステムプロンプト(キャラクター設定)として読み込まれる。
感情タグは `<<感情名>>` 形式で応答先頭に付与される想定:

```
<<嬉しい>>わぁ、コメントありがとう！うれしいな〜
```

`<<...>>` 内の文字列が Diffmotion のプリセット名として `switch_preset()` に渡されるため、Diffmotion 側のプリセット名と一致させる必要がある。

## Supporters

[![note メンバーシップ](https://img.shields.io/badge/note-Membership-41C9B4?style=for-the-badge&logo=note&logoColor=white)](https://note.com/yuki_tech/membership/members)

## License

Copyright (c) 2026 [yuki-P](https://x.com/yuki_p02)
Licensed under the [MIT License](LICENSE).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
