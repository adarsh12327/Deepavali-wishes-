import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN")
REDIS_URL = os.environ.get("REDIS_URL")

if not BOT_TOKEN:
    raise RuntimeError("Missing BOT_TOKEN environment variable")
if not REDIS_URL:
    raise RuntimeError("Missing REDIS_URL environment variable")

bot = Bot(token=BOT_TOKEN)
storage = RedisStorage.from_url(REDIS_URL)
dp = Dispatcher(storage=storage)


class ProfileForm(StatesGroup):
    display_name = State()
    username = State()
    bio = State()


def start_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Create profile draft", callback_data="make_draft")],
        [InlineKeyboardButton(text="📸 Open Instagram", url="https://www.instagram.com/")]
    ])


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Welcome to Instagram Profile Helper!\n\n"
        "Main aapke Instagram profile ke liye name, username idea aur bio ka draft banaunga.\n"
        "⚠️ Instagram account bot khud create nahi kar sakta. Registration aur verification aap official Instagram app/site par khud karein.\n"
        "Apna password, OTP ya email yahan mat bhejein.",
        reply_markup=start_keyboard()
    )


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Process cancel ho gaya. Dobara shuru karne ke liye /start bhejein.")


@dp.callback_query(F.data == "make_draft")
async def begin_profile(callback, state: FSMContext):
    await state.clear()
    await state.set_state(ProfileForm.display_name)
    await callback.message.answer("1/3 — Profile par dikhane wala naam likhein:")
    await callback.answer()


@dp.message(ProfileForm.display_name)
async def get_display_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not name or len(name) > 60:
        await message.answer("Naam 1–60 characters ka likhein.")
        return
    await state.update_data(display_name=name)
    await state.set_state(ProfileForm.username)
    await message.answer("2/3 — Apna pasandida username idea likhein (sirf suggestion; availability check nahi hoti):")


@dp.message(ProfileForm.username)
async def get_username(message: Message, state: FSMContext):
    username = (message.text or "").strip().lstrip("@")
    if not username or len(username) > 30 or not all(c.isalnum() or c in "._" for c in username):
        await message.answer("Username idea mein letters, numbers, dot ya underscore use karein (max 30 characters).")
        return
    await state.update_data(username=username)
    await state.set_state(ProfileForm.bio)
    await message.answer("3/3 — Instagram bio likhein (max 150 characters):")


@dp.message(ProfileForm.bio)
async def get_bio(message: Message, state: FSMContext):
    bio = (message.text or "").strip()
    if len(bio) > 150:
        await message.answer("Bio Instagram bio limit ke andar rakhein (150 characters max).")
        return

    data = await state.get_data()
    name = data.get("display_name", "")
    username = data.get("username", "")
    await state.clear()

    draft = (
        "✅ Aapka Instagram profile draft ready hai!\n\n"
        f"👤 Name: {name}\n"
        f"🔖 Username idea: @{username}\n"
        f"📝 Bio: {bio or '(bio blank chhodi gayi)'}\n\n"
        "Next step: Instagram par khud sign up karein aur available username choose karein.\n"
        "Password, email verification aur OTP sirf official Instagram app/site par enter karein."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Open Instagram signup", url="https://www.instagram.com/accounts/emailsignup/")],
        [InlineKeyboardButton(text="Make another draft", callback_data="make_draft")]
    ])
    await message.answer(draft, reply_markup=keyboard)


@dp.message()
async def fallback(message: Message):
    await message.answer("Shuru karne ke liye /start bhejein. Process rokne ke liye /cancel.")
