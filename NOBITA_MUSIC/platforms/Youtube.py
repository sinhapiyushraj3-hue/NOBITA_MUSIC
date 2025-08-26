import asyncio
import os
import re
from typing import Union
import requests  # Added import for requests

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from NOBITA_MUSIC.utils.database import is_on_off
from NOBITA_MUSIC.utils.formatters import time_to_seconds


def cookies():
    """
    Fetches cookies from a specified URL and saves them to a local file.
    Deletes the old cookies.txt file if it exists before downloading a new one.
    """
    url = "https://v0-mongo-db-api-setup.vercel.app/api/cookies.txt"
    filename = "cookies.txt"

    # Delete the file if it already exists
    if os.path.exists(filename):
        os.remove(filename)

    # Download the file from the URL
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        return filename
    else:
        raise Exception("Failed to fetch cookies from URL")

# Fetch cookies and set the file path
cookies_file = cookies()


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = (
                int(time_to_seconds(duration_min))
                if duration_min
                else 0
            )
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]
        return None

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]
        return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
        return None

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookies_file,
            "-g",
            "-f",
            "best[height<=720][width<=1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        async def shell_cmd(cmd):
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, errorz = await proc.communicate()
            if errorz and "unavailable videos are hidden" not in (errorz.decode("utf-8")).lower():
                # Handle or log the error appropriately
                return ""
            return out.decode("utf-8")

        playlist_cmd = (
            f"yt-dlp --cookies {cookies_file} -i --get-id --flat-playlist "
            f"--playlist-end {limit} --skip-download {link}"
        )
        playlist = await shell_cmd(playlist_cmd)
        
        return [item for item in playlist.split("\n") if item]


    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            track_details = {
                "title": result["title"],
                "link": result["link"],
                "vidid": result["id"],
                "duration_min": result["duration"],
                "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }
            return track_details, result["id"]
        return None, None

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile": cookies_file}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        formats_available = []
        with ydl:
            r = ydl.extract_info(link, download=False)
            for f in r.get("formats", []):
                if "dash" not in str(f.get("format", "")).lower():
                    try:
                        formats_available.append({
                            "format": f["format"],
                            "filesize": f.get("filesize"),
                            "format_id": f["format_id"],
                            "ext": f["ext"],
                            "format_note": f.get("format_note"),
                            "yturl": link,
                        })
                    except KeyError:
                        continue
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result", [])
        if result and len(result) > query_type:
            res = result[query_type]
            title = res["title"]
            duration_min = res["duration"]
            vidid = res["id"]
            thumbnail = res["thumbnails"][0]["url"].split("?")[0]
            return title, duration_min, thumbnail, vidid
        return None, None, None, None


    async def download(
        self,
        link: str,
        mystic,
        video: bool = False,
        videoid: bool = False,
        songaudio: bool = False,
        songvideo: bool = False,
        format_id: str = None,
        title: str = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()
        
        base_ydl_opts = {
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": cookies_file,
        }

        def download_action(opts):
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                download_path = ydl.prepare_filename(info)
                if not os.path.exists(download_path):
                    ydl.download([link])
                return download_path

        if songvideo:
            opts = {
                **base_ydl_opts,
                "format": f"{format_id}+bestaudio[ext=m4a]/best",
                "outtmpl": f"downloads/{title}.mp4",
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            return await loop.run_in_executor(None, download_action, opts)

        elif songaudio:
            opts = {
                **base_ydl_opts,
                "format": format_id,
                "outtmpl": f"downloads/{title}.%(ext)s",
                "prefer_ffmpeg": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            # yt-dlp will add the .mp3 extension
            downloaded_file = await loop.run_in_executor(None, download_action, opts)
            return os.path.splitext(downloaded_file)[0] + ".mp3"

        elif video:
            opts = {
                **base_ydl_opts,
                "format": "(bestvideo[height<=720][width<=1280][ext=mp4])+(bestaudio[ext=m4a])/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "merge_output_format": "mp4",
            }
            return await loop.run_in_executor(None, download_action, opts), True

        else: # Default to audio
            opts = {
                **base_ydl_opts,
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
            }
            return await loop.run_in_executor(None, download_action, opts), True
