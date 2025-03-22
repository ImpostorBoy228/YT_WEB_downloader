import os
import json
import requests
import isodate
from pytube import YouTube
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from datetime import datetime


import yt_dlp


# Конфигурация
CONFIG = {
    "storage_path": "/mnt/d/videos",
    "db_uri": "postgresql://impostorboy:0@localhost/youtube_backup",
    "service_account_file": "/home/impostorboy/downlader/service_account.json"
}

# Подключение к базе данных
engine = create_engine(CONFIG['db_uri'])
db = scoped_session(sessionmaker(bind=engine))

# Авторизация через сервисный аккаунт
def get_youtube_service():
    credentials = service_account.Credentials.from_service_account_file(
        CONFIG['service_account_file'],
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
    )
    return build('youtube', 'v3', credentials=credentials)

# Конвертация ISO 8601 -> секунды
def parse_duration(duration):
    try:
        return int(isodate.parse_duration(duration).total_seconds())
    except:
        return 0

# Сохранение данных о видео в БД
def save_video_to_db(video_id, title, description, uploader, views, duration, upload_date):
    try:
        db.execute(text("""
            INSERT INTO videos (id, title, description, uploader, views, duration, upload_date)
            VALUES (:id, :title, :description, :uploader, :views, :duration, :upload_date)
            ON CONFLICT (id) DO NOTHING;
        """), {
            "id": video_id,
            "title": title,
            "description": description,
            "uploader": uploader,
            "views": views,
            "duration": duration,
            "upload_date": datetime.strptime(upload_date, '%Y-%m-%dT%H:%M:%SZ')
        })
        db.commit()
        print(f"✅ Видео '{title}' добавлено в базу данных.")
    except Exception as e:
        print(f"❌ Ошибка при добавлении видео в базу данных: {e}")

# Загрузка превью
def download_thumbnail(thumbnail_url, thumbnail_path):
    try:
        print(f"Загружаем превью с URL: {thumbnail_url}")
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            with open(thumbnail_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Превью загружено: {thumbnail_path}")
        else:
            print("❌ Не удалось скачать превью.")
    except Exception as e:
        print(f"❌ Ошибка при загрузке превью: {e}")

# Получение данных о видео из YouTube API
def get_video_info(video_url):
    try:
        video_id = video_url.split("v=")[1].split("&")[0]

        youtube = get_youtube_service()
        video_request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )
        video_response = video_request.execute()

        if not video_response['items']:
            print("❌ Не удалось найти видео.")
            return None, None, None

        video_data = video_response['items'][0]
        video_title = video_data['snippet']['title']
        description = video_data['snippet']['description']
        uploader = video_data['snippet']['channelTitle']
        views = int(video_data['statistics'].get('viewCount', 0))
        duration = parse_duration(video_data['contentDetails']['duration'])
        upload_date = video_data['snippet']['publishedAt']
        
        video_file_path = f"{CONFIG['storage_path']}/{video_id}.webm"
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        thumbnail_path = f"{CONFIG['storage_path']}/{video_id}.webp"

        download_thumbnail(thumbnail_url, thumbnail_path)
        save_video_to_db(video_id, video_title, description, uploader, views, duration, upload_date)

        return video_title, video_file_path

    except HttpError as e:
        print(f"❌ Ошибка API: {e}")
        return None, None

# Загрузка видео с помощью yt-dlp
def download_video(video_url):
    video_title, video_file_path = get_video_info(video_url)

    if video_title:
        print(f"✅ Видео '{video_title}' найдено. Начинаю загрузку...")

        output_template = f"{CONFIG['storage_path']}/%(id)s.%(ext)s"
        ydl_opts = {
            'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/best',
            'outtmpl': output_template,
            'merge_output_format': 'webm',
            'noplaylist': True,
            'quiet': False,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            print(f"✅ Видео успешно загружено.")
        except Exception as e:
            print(f"❌ Ошибка при загрузке видео: {e}")
    else:
        print("❌ Не удалось скачать видео.")
# Основная функция
def main():
    video_url = input("Введите ссылку на видео YouTube: ")
    download_video(video_url)

if __name__ == "__main__":
    main()
