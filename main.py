import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

BOT_TOKEN = "7750912634:AAFKT2PaI4BJKKx58QYdZBp1XxPXYkYve94"
ADMINS = [6733100026]
CHANNELS = ["@shaxsiy_blog1o", "@kinoda23"]

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

videos = {}
users = set()

@dp.message(Command("start"))
async def start_cmd(msg: Message):
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, msg.from_user.id)
            if member.status not in ["member", "administrator", "creator"]:
                raise Exception("Not subscribed")
        except:
            btn = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ Obuna bo‘lish", url=f"https://t.me/{ch[1:]}")]
            ])
            return await msg.answer(f"⛔ Botdan foydalanish uchun {ch} kanaliga obuna bo‘ling!", reply_markup=btn)

    users.add(msg.from_user.id)
    await msg.answer("🎬 Video ID raqamini yuboring.\nAgar admin bo‘lsangiz video yuboring.")

@dp.message(F.video)
async def upload_video(msg: Message):
    if msg.from_user.id not in ADMINS:
        return await msg.answer("⛔ Siz admin emassiz.")
    
    await msg.answer("📥 Iltimos, ushbu video uchun Nomi va Kodni quyidagicha yuboring:\n\n<pre>Nom = Kod</pre>")

    @dp.message()
    async def save_video(data: Message):
        if "=" in data.text:
            name, code = map(str.strip, data.text.split("=", 1))
            video_id = msg.video.file_id
            videos[code] = {"file_id": video_id, "name": name}
            await data.answer(f"✅ Video saqlandi!\n🎬 {name} (KOD: {code})")

            # Foydalanuvchilarga xabar yuborish
            for uid in users:
                try:
                    await bot.send_message(uid, f"📽 Yangi video yuklandi:\n🎬 <b>{name}</b>\nID: <code>{code}</code>")
                except TelegramBadRequest:
                    pass
        else:
            await data.answer("❌ Noto‘g‘ri format. To‘g‘ri format: <pre>Nom = Kod</pre>")

@dp.message(F.text)
async def send_video(msg: Message):
    code = msg.text.strip()
    if code in videos:
        file_id = videos[code]["file_id"]
        name = videos[code]["name"]
        await msg.answer_video(video=file_id, caption=f"🎬 {name} (ID: {code})")
    elif msg.text.lower() == "stat":
        if msg.from_user.id in ADMINS:
            await msg.answer(f"👥 Foydalanuvchilar soni: {len(users)}")
        else:
            await msg.answer("⛔ Ruxsat yo‘q.")
    else:
        await msg.answer("😕 Bunday kodli video topilmadi.")
