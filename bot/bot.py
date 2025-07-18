import os

from dotenv import load_dotenv
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))