import asyncio, json, re, time
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Callable, Dict, Any, Awaitable
import config, db, texts

db.init_db()
bot = Bot(token=config.BOT_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher(storage=MemoryStorage())

# --- Middleware для блокировки пользователей ---
class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        user_id = getattr(event, 'from_user', None).id if hasattr(event, 'from_user') else None
        if user_id:
            try:
                with open(config.BANNED_FILE, 'r') as f:
                    banned = json.load(f)
                if user_id in banned:
                    if isinstance(event, Message):
                        await event.answer(texts.BotTexts.TEXT_USER_BLOCKED)
                    return
            except: pass
        return await handler(event, data)

dp.message.outer_middleware(BanMiddleware())
dp.callback_query.outer_middleware(BanMiddleware())

# --- Хелпер для экранирования спецсимволов MarkdownV2 ---
def escape_md(text):
    if not text: return ""
    escape_chars = r'\_*[]()~`>#+=|{}.!'
    return ''.join('\\' + c if c in escape_chars else c for c in text)

# --- Отправка поста админу с клавиатурой модерации ---
async def send_post_to_admins(post_id, user_id, username, content_type, content, footer):
    from_user = await bot.get_chat(user_id)
    full_name = from_user.full_name
    mention = f"[{escape_md(full_name)}](tg://user?id={user_id})"
    content_summary = f"{escape_md(username)} ({mention}) отправил(а): {content[:50]}..."
    post_text = texts.BotTexts.pending_post_text(post_id, user_id, username, escape_md(content_summary))
    keyboard = texts.BotTexts.moderation_keyboard(post_id)
    if content_type.startswith("media_group_"):
        # Сохраняем список file_id для медиагруппы
        await bot.send_message(config.ADMIN_IDS[0], post_text, reply_markup=keyboard)
        # Здесь нужна дополнительная логика для отправки медиагрупп
    elif content_type == 'text':
        await bot.send_message(config.ADMIN_IDS[0], post_text + f"\n\n{escape_md(content)}", reply_markup=keyboard)
    elif content_type == 'photo':
        await bot.send_photo(config.ADMIN_IDS[0], content, caption=post_text, reply_markup=keyboard)
    elif content_type == 'video':
        await bot.send_video(config.ADMIN_IDS[0], content, caption=post_text, reply_markup=keyboard)
    elif content_type == 'document':
        await bot.send_document(config.ADMIN_IDS[0], content, caption=post_text, reply_markup=keyboard)
    # Обработка других типов

# --- Обработка всех входящих сообщений от пользователей ---
@dp.message()
async def handle_post(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "no_username"
    footer = db.get_setting("post_footer")
    # Обработка медиагруппы
    if message.media_group_id:
        # Логика сбора всех медиа из группы
        pass
    elif message.text:
        content = message.text
        post_id = db.add_post(user_id, username, 'text', content, footer)
        await send_post_to_admins(post_id, user_id, username, 'text', content, footer)
        await message.answer("✅ Ваш пост отправлен на модерацию!")
    elif message.photo:
        file_id = message.photo[-1].file_id
        post_id = db.add_post(user_id, username, 'photo', file_id, footer)
        await send_post_to_admins(post_id, user_id, username, 'photo', file_id, footer)
        await message.answer("✅ Ваше фото отправлено на модерацию!")
    elif message.video:
        file_id = message.video.file_id
        post_id = db.add_post(user_id, username, 'video', file_id, footer)
        await send_post_to_admins(post_id, user_id, username, 'video', file_id, footer)
        await message.answer("✅ Ваше видео отправлено на модерацию!")
    elif message.document:
        file_id = message.document.file_id
        post_id = db.add_post(user_id, username, 'document', file_id, footer)
        await send_post_to_admins(post_id, user_id, username, 'document', file_id, footer)
        await message.answer("✅ Ваш документ отправлен на модерацию!")

# --- Callback для одобрения/отклонения ---
@dp.callback_query(F.data.startswith("approve_"))
async def approve_post(callback: CallbackQuery):
    post_id = int(callback.data.split("_")[1])
    post = db.get_post_by_id(post_id)
    if post:
        content_type = post[3]
        content = post[4]
        footer = db.get_setting("post_footer")
        if footer:
            footer = "\n\n" + footer
        try:
            if content_type == 'text':
                await bot.send_message(config.CHANNEL_ID, f"{content}{footer}")
            elif content_type == 'photo':
                await bot.send_photo(config.CHANNEL_ID, content, caption=footer)
            elif content_type == 'video':
                await bot.send_video(config.CHANNEL_ID, content, caption=footer)
            elif content_type == 'document':
                await bot.send_document(config.CHANNEL_ID, content, caption=footer)
            db.delete_post(post_id)
            await callback.answer(texts.BotTexts.TEXT_POST_APPROVED)
        except Exception as e:
            await callback.answer(f"Ошибка: {e}")
    await callback.message.delete()

@dp.callback_query(F.data.startswith("reject_"))
async def reject_post(callback: CallbackQuery):
    post_id = int(callback.data.split("_")[1])
    db.delete_post(post_id)
    await callback.answer(texts.BotTexts.TEXT_POST_REJECTED)
    await callback.message.delete()

# --- Админ-панель и другие обработчики (блокировка, изменение текстов) ---
# (Остальные функции админ-панели, блокировки, изменения текстов и т.д.)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
