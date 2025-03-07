from aiogram import Dispatcher
from task1.handlers.voice_handler import register_voice_handler
from task1.handlers.start_handler import register_start_handler
from task1.handlers.image_handler import register_image_handler

def register_handlers(dp:Dispatcher):
    register_voice_handler(dp)
    register_start_handler(dp)
    register_image_handler(dp)

