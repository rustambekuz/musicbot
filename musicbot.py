import html
import logging
import os
import subprocess

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
load_dotenv()

from aiohttp import ClientSession
from aiogram import F

API_TOKEN=os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def update_yt_dlp():
    try:
        subprocess.run(
            ["python3", "-m", "pip", "install", "--upgrade", "yt-dlp"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logger.info("yt-dlp successfully updated.")
    except subprocess.CalledProcessError:
        logger.warning("yt-dlp update failed.")

update_yt_dlp()


def download_audio(query: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        filename = ydl.prepare_filename(info['entries'][0])
        mp3_filename = filename.rsplit('.', 1)[0] + ".mp3"
        return mp3_filename, info['entries'][0]['title']


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("🎧 Salom! Menga musiqa nomini yozing.\nMasalan: `Jaloliddin Ahmadaliyev - janona`", parse_mode=ParseMode.HTML)


@dp.message(F.text)
async def handle_music(message: Message):
    query = message.text
    await message.answer(
        f"⏳ <b>Qo‘shiq izlanmoqda...</b>\n🎧 <i>{query}</i>",
        parse_mode="HTML"
    )


    try:
        file_path, title = download_audio(query)
        await message.answer_audio(types.FSInputFile(file_path), title=title)
        os.remove(file_path)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Musiqa yuklab olinmadi. Iltimos, boshqa nomni kiriting.")


if __name__ == "__main__":
    dp.run_polling(bot)
