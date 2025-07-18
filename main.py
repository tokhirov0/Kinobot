import logging import os from aiogram import Bot, Dispatcher, F, types from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton from aiogram.enums import ParseMode from aiogram.filters import CommandStart, Command from aiogram.utils.markdown import hbold from aiogram.utils.keyboard import ReplyKeyboardBuilder from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") ADMIN_ID = int(os.getenv("ADMIN_ID")) CHANNELS = ["@shaxsiy_blog1o", "@kinoda23"]

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML) dp = Dispatcher()

videos = {} users = set()

keyboard = ReplyKeyboardMarkup( keyboard=[[KeyboardButton(text="📽 Kino izlash")]], resize_keyboard=True )

@dp.message(CommandStart()) async def start_handler(message: Message): users.add(message.chat.id) await message.answer(f"Salom {hbold(message.from_user.first_name)}!\nID raqam orqali kino izlash uchun tugmani bosing.", reply_markup=keyboard)

@dp.message(Command("add")) async def add_video(message: Message): if message.chat.id != ADMIN_ID: return if not message.reply_to_message or not message.reply_to_message.video: await message.answer("Iltimos, kinoga javoban /add deb yozing.") return

video = message.reply_to_message.video
caption = message.reply_to_message.caption or ""
video_id = len(videos) + 1
videos[video_id] = {"file_id": video.file_id, "caption": caption}

for user_id in users:
    try:
        await bot.send_video(user_id, video.file_id, caption=f"<b>Yangi kino qo‘shildi!</b>\n🎬 Nomi: {caption}\n🆔 ID: {video_id}")
    except Exception as e:
        logging.error(f"Xatolik foydalanuvchiga yuborishda: {e}")

await message.answer(f"Kino qo‘shildi! ID: {video_id}")

@dp.message(Command("delete")) async def delete_video(message: Message): if message.chat.id != ADMIN_ID: return parts = message.text.split() if len(parts) != 2 or not parts[1].isdigit(): await message.answer("To‘g‘ri format: /delete 5") return video_id = int(parts[1]) if video_id in videos: del videos[video_id] await message.answer(f"Kino o‘chirildi: ID {video_id}") else: await message.answer("Bunday ID topilmadi.")

@dp.message(Command("stats")) async def stats(message: Message): if message.chat.id == ADMIN_ID: await message.answer(f"📊 Foydalanuvchilar soni: {len(users)}\n🎞 Kinolar soni: {len(videos)}")

@dp.message(F.text.regexp("^\d+$")) async def send_video_by_id(message: Message): video_id = int(message.text) video = videos.get(video_id) if video: await message.answer_video(video["file_id"], caption=video["caption"]) else: await message.answer("Bunday ID topilmadi. Iltimos, boshqa raqam kiriting.")

if name == 'main': import asyncio logging.basicConfig(level=logging.INFO) asyncio.run(dp.start_polling(bot))

