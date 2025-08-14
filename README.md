# YT_WEB_downloader

A lightweight tool for parsing and downloading YouTube videos from the web.

## Features

- Download YouTube videos via URL.
- Video metadata parsing.
- Command-line interface for quick usage.
- Lightweight, minimal dependencies.

## Installation

```bash
git clone https://github.com/ImpostorBoy228/YT_WEB_downloader.git
cd YT_WEB_downloader
pip install -r requirements.txt
```

## Usage

```bash
python downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Codebase Overview

- `downloader.py`: Handles video downloads and CLI.
- `parser.py`: Extracts video metadata from YouTube.
- `requirements.txt`: Dependencies (`pytube`, etc).

## Troubleshooting

- Make sure your Python version is 3.7+.
- If an error occurs, check that `pytube` is up to date.

## License

MIT
