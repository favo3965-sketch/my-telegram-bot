import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

API_TOKEN = "8915509285:AAFsZwLlzCDk9UheAq6k78L91LB7CT4j5-M"

ALLOWED_IDS = [7110404642, 1042812347]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

users_data = {}


def get_user_storage(user_id: int):
    """Создает личную папку для пользователя, если её еще нет"""
    if user_id not in users_data:
        users_data[user_id] = {"images": [], "music": [], "text": []}
    return users_data[user_id]

@dp.message.outer_middleware()
async def limit_access(handler, event: types.Message, data):
    if event.from_user.id not in ALLOWED_IDS:
        await event.answer("⛔ Это приватный бот.")
        return
    return await handler(event, data)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🖼 Изображения"), KeyboardButton(text="🎵 Музыка")],
        [KeyboardButton(text="📝 Текст")],
    ],
    resize_keyboard=True,
)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    get_user_storage(message.from_user.id)
    await message.answer(
        "Привет! Это твое личное изолированное хранилище.\n"
        "Отправляй мне любые фото, треки или текст — я всё сохраню только для тебя.\n"
        "Жми на кнопки ниже, чтобы посмотреть сохранённое!",
        reply_markup=main_keyboard,
    )

@dp.message(F.text == "🖼 Изображения")
async def show_images(message: types.Message):
    storage = get_user_storage(message.from_user.id)
    if not storage["images"]:
        await message.answer("🖼 У тебя пока нет сохраненных картинок. Просто скинь мне фото!")
        return

    await message.answer(
        f"🖼 *Твои сохраненные фото ({len(storage['images'])} шт.):*",
        parse_mode="Markdown",
    )
    for photo_id in storage["images"]:
        await message.answer_photo(photo=photo_id)


@dp.message(F.text == "🎵 Музыка")
async def show_music(message: types.Message):
    storage = get_user_storage(message.from_user.id)
    if not storage["music"]:
        await message.answer("🎵 У тебя пока нет сохраненных треков. Скинь мне аудиозапись или голосовое!")
        return

    await message.answer(
        f"🎵 *Твои сохраненные аудиозаписи ({len(storage['music'])} шт.):*",
        parse_mode="Markdown",
    )
    for audio_id in storage["music"]:
        await message.answer_audio(audio=audio_id)


@dp.message(F.text == "📝 Текст")
async def show_text(message: types.Message):
    storage = get_user_storage(message.from_user.id)
    if not storage["text"]:
        await message.answer("📝 Заметок пока нет. Напиши мне любое сообщение, и я его сохраню!")
        return

    notes = "\n\n---\n\n".join([f"• {note}" for note in storage["text"]])
    await message.answer(
        f"📝 *Твои сохраненные заметки:*\n\n{notes}",
        parse_mode="Markdown",
    )

@dp.message(F.photo)
async def save_photo(message: types.Message):
    storage = get_user_storage(message.from_user.id)
    photo_id = message.photo[-1].file_id
    storage["images"].append(photo_id)
    await message.answer("✅ Фото успешно сохранено в твои «🖼 Изображения»!")


@dp.message(F.audio | F.voice)
async def save_audio(message: types.Message):
    storage = get_user_storage(message.from_user.id)
    file_id = message.audio.file_id if message.audio else message.voice.file_id
    storage["music"].append(file_id)
    await message.answer("✅ Аудио успешно сохранено в твою «🎵 Музыка»!")


@dp.message(F.text & ~F.text.in_(["🖼 Изображения", "🎵 Музыка", "📝 Текст"]))
async def save_note(message: types.Message):
    storage = get_user_storage(message.from_user.id)
    storage["text"].append(message.text)
    await message.answer("✅ Заметка успешно сохранена в твой «📝 Текст»!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    