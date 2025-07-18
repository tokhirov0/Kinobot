import logging import asyncio import os from aiogram import Bot, Dispatcher, F from aiogram.enums import ParseMode from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton from aiogram.filters import CommandStart, Command

API_TOKEN = os.getenv("BOT_TOKEN") ADMIN_ID = 6733100026 CHANNELS = ["@shaxsiy_blog1o", "@kinoda23"]

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML) dp = Dispatcher()

Fayllar bazasi (memory uchun, Render'da DB o'rniga vaqtincha ishlatamiz)

movies = {} users = set() admin_ids = {ADMIN_ID}

Inline button - obuna tekshiruvi

async def check_sub_channels(user_id): for ch in CHANNELS: try: member = await bot.get_chat_member(chat_id=ch, user_id=user_id) if member.status in ("left", "kicked"): return False except: return False return True

def subscribe_keyboard(): btns = [ [InlineKeyboardButton(text=f"📢 {ch}", url=f"https://t.me/{ch[1:]}")] for ch in CHANNELS ] btns.append([InlineKeyboardButton(text="✅ Tekshirdim", callback_data="check_sub")]) return InlineKeyboardMarkup(inline_keyboard=btns)

Start komandasi

@dp.message(CommandStart()) async def cmd_start(message: Message): users.add(message.from_user.id) if not await check_sub_channels(message.from_user.id): await message.answer("Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=subscribe_keyboard()) return await message.answer("🎬 Kino raqamini yuboring yoki /panel orqali film yuklang")

Video ID yuborilganda

@dp.message(F.text.regexp(r"^\d+$")) async def get_movie(message: Message): if not await check_sub_channels(message.from_user.id): await message.answer("⛔ Avval kanallarga obuna bo‘ling:", reply_markup=subscribe_keyboard()) return movie_id = int(message.text) movie = movies.get(movie_id) if movie: await message.answer_video(video=FSInputFile(movie["file"]), caption=f"🎬 <b>{movie['title']}</b>") else: await message.answer("❌ Bunday raqamli kino topilmadi.")

Admin panel

@dp.message(Command("panel")) async def admin_panel(message: Message): if message.from_user.id in admin_ids: await message.answer("📥 Kino yuboring: Avval nomini yozing, keyin videoni jo'nating") else: await message.answer("⛔ Bu buyruq faqat admin uchun.")

Video qabul qilish

current_titles = {}

@dp.message(F.video) async def receive_video(message: Message): if message.from_user.id not in admin_ids: return title = current_titles.get(message.from_user.id) if not title: await message.answer("⛔ Avval kino nomini yozing") return file = await bot.download(message.video.file_id, destination=f"videos/{message.video.file_id}.mp4") movie_id = len(movies) + 1 movies[movie_id] = {"title": title, "file": file.name} await message.answer(f"✅ Kino saqlandi! Raqami: <b>{movie_id}</b>") # Notify all users for uid in users: try: await bot.send_message(uid, f"🆕 Yangi kino qo‘shildi: <b>{title}</b>\nKo‘rish uchun raqam: <b>{movie_id}</b>") except: continue del current_titles[message.from_user.id]

@dp.message(F.text) async def save_title(message: Message): if message.from_user.id in admin_ids: current_titles[message.from_user.id] = message.text await message.answer("✅ Endi kinoni yuboring")

Subscribe button tekshirish

@dp.callback_query(F.data == "check_sub") async def check_sub_callback(callback): if await check_sub_channels(callback.from_user.id): await callback.message.delete() await callback.message.answer("✅ Tashakkur! Endi botdan foydalanishingiz mumkin.") else: await callback.answer("⛔ Hali ham obuna bo‘lmagansiz!", show_alert=True)

Run

async def main(): logging.basicConfig(level=logging.INFO) os.makedirs("videos", exist_ok=True) await dp.start_polling(bot)

if name == 'main': asyncio.run(main())

