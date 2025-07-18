import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import json
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNELS = os.getenv("CHANNELS").split(',')

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

DATA_FILE = "videos.json"
USERS_FILE = "users.json"

class AddVideo(StatesGroup):
    waiting_for_title = State()

video_data = {}

# === Foydalanuvchini saqlash ===
async def save_user(user_id):
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

# === Video ma'lumotlarini saqlash ===
def load_videos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_videos(videos):
    with open(DATA_FILE, 'w') as f:
        json.dump(videos, f)

videos = load_videos()

# === /start ===
@dp.message(CommandStart())
async def start(message: Message):
    await save_user(message.from_user.id)
    await message.answer("🎬 Assalomu alaykum! Kino ID raqamini yuboring, men sizga videoni jo'nataman.")

# === Admin video yuborsa ===
@dp.message(F.video)
async def handle_video(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Siz admin emassiz.")
    file_id = message.video.file_id
    video_data[message.from_user.id] = file_id
    await message.answer("📌 Kino nomini kiriting:")
    await state.set_state(AddVideo.waiting_for_title)

# === Kino nomini yozganda ===
@dp.message(AddVideo.waiting_for_title)
async def set_title(message: Message, state: FSMContext):
    title = message.text
    user_id = message.from_user.id
    file_id = video_data.get(user_id)
    if not file_id:
        return await message.answer("Xatolik yuz berdi.")
    
    video_id = str(len(videos) + 1)
    videos[video_id] = {"file_id": file_id, "title": title}
    save_videos(videos)

    # Xabar yuborish
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except:
        users = []

    for uid in users:
        try:
            await bot.send_message(uid, f"🎬 <b>Yangi kino:</b> {title}\n📥 ID: <code>{video_id}</code>")
        except:
            pass

    await message.answer(f"✅ Kino saqlandi!\nID: <code>{video_id}</code>")
    await state.clear()

# === Foydalanuvchi ID yuborsa ===
@dp.message(F.text.regexp(r"^\d+$"))
async def send_video_by_id(message: Message):
    await save_user(message.from_user.id)

    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(channel, message.from_user.id)
        if chat_member.status not in ['member', 'administrator', 'creator']:
            return await message.answer(f"⛔️ Avval quyidagi kanalga a'zo bo'ling:\n@{channel}")

    vid_id = message.text.strip()
    if vid_id not in videos:
        return await message.answer("❌ Bunday ID topilmadi.")
    
    file_id = videos[vid_id]["file_id"]
    title = videos[vid_id]["title"]
    await message.answer_video(file_id, caption=f"🎬 {title}")

# === Statistika ===
@dp.message(F.text == "/stat" or F.text == "📊 Statistika")
async def stat(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        count = len(users)
    except:
        count = 0
    await message.answer(f"📊 Bot foydalanuvchilari soni: <b>{count}</b>")
