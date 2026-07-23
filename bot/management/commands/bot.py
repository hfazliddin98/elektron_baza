"""Telegram botni ishga tushiradi: `python manage.py bot`.

Serverda systemd xizmati sifatida doimiy ishlab turadi (deploy/ papkasiga qarang).
Token `.env` dagi BOT_TOKEN da bo'lishi kerak.
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from bot.handlers import router


async def ishga_tushir(token):
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    malumot = await bot.get_me()
    logging.info('Bot ishga tushdi: @%s', malumot.username)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


class Command(BaseCommand):
    help = 'Telegram botni ishga tushiradi (polling rejimida)'

    def handle(self, *args, **options):
        token = settings.BOT_TOKEN
        if not token:
            raise CommandError(
                "BOT_TOKEN sozlanmagan. .env fayliga BotFather bergan tokenni yozing."
            )

        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
        )
        self.stdout.write(self.style.SUCCESS('Bot ishga tushmoqda... (to\'xtatish: Ctrl+C)'))
        try:
            asyncio.run(ishga_tushir(token))
        except KeyboardInterrupt:
            self.stdout.write('Bot to\'xtatildi.')
