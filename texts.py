from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class BotTexts:
    TEXT_START = ("✍️ Отправь мне текст, фото, видео или другой медиафайл — "
                  "я передам его на модерацию в канал.")
    TEXT_HELP = "Отправь контент, я покажу его админам для публикации."
    TEXT_USER_BLOCKED = "⛔ Вы заблокированы."
    TEXT_REPLY_RECEIVED = "✅ Ваш ответ отправлен автору поста."
    TEXT_ADMIN_REPLY_SENT = "✅ Ответ отправлен пользователю."
    TEXT_ADMIN_ONLY = "⚠️ Доступно только админам."
    TEXT_INVALID_REPLY_ID = "❌ Некорректный ID поста."
    TEXT_POST_APPROVED = "✅ Пост опубликован."
    TEXT_POST_REJECTED = "❌ Пост отклонён."
    TEXT_NO_PENDING_POSTS = "Нет постов на модерации."

    @staticmethod
    def pending_post_text(post_id: int, user_id: int, username: str, content_summary: str) -> str:
        return (f"📨 **Новый пост**\n"
                f"ID поста: `{post_id}`\n👤 Юзернейм: @{username}\n🆔 Telegram ID: `{user_id}`\n"
                f"📄 **Содержание**: {content_summary}")
    @staticmethod
    def admin_panel_text() -> str:
        return "⚙️ **Админ-панель**\nВыберите действие:"
    @staticmethod
    def admin_panel_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Посты на модерации", callback_data="admin_pending_posts"),
             InlineKeyboardButton(text="🚷 Блокировка пользователей", callback_data="admin_ban_menu")],
            [InlineKeyboardButton(text="✏️ Изменить сообщения бота", callback_data="admin_change_texts"),
             InlineKeyboardButton(text="🔗 Изменить подпись к посту", callback_data="admin_change_footer")]
        ])
    @staticmethod
    def moderation_keyboard(post_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{post_id}"),
             InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{post_id}")],
            [InlineKeyboardButton(text="💬 Ответить автору в ЛС", callback_data=f"reply_to_author_{post_id}")]
        ])
    @staticmethod
    def pending_posts_keyboard(posts: list, page: int = 0) -> InlineKeyboardMarkup:
        keyboard = []
        for i, (pid, uid, uname) in enumerate(posts[page*5:(page+1)*5]):
            keyboard.append([InlineKeyboardButton(text=f"📄 {pid} от @{uname}", callback_data=f"open_post_{pid}")])
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"pending_page_{page-1}"))
        if len(posts) > (page+1)*5:
            nav_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"pending_page_{page+1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton(text="🔙 В админ-панель", callback_data="admin_panel")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)