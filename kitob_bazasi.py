import sqlite3
import telebot
from telebot import types
import os

# ==========================================
# 🔑 SOZLAMALAR
# ==========================================

TOKEN = "8806238942:AAEhQsLhVHtncIVlvrKjgrBVYUBwKtHMLeU"

ADMIN_ID = 8694801795

# 📢 Kitoblar yuboriladigan guruh
GROUP_ID = -1003753451546

# 📚 Baza guruhi
DATABASE_ID = -1003922628168


# ==========================================
# 🤖 BOT
# ==========================================

bot = telebot.TeleBot(TOKEN)


# ==========================================
# 📚 SQLITE BAZA
# ==========================================

conn = sqlite3.connect(
    "books.db",
    check_same_thread=False
)

cursor = conn.cursor()


# Kitoblar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    telegram_file_id TEXT NOT NULL UNIQUE
)
""")


# Foydalanuvchilar jadvali
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT
)
""")

conn.commit()


# ==========================================
# 👤 ASOSIY MENYU
# ==========================================

def main_keyboard():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        types.KeyboardButton("🔎 Kitob qidirish")
    )

    return keyboard


# ==========================================
# ⚙️ ADMIN MENYU
# ==========================================

def admin_keyboard():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        types.KeyboardButton("📤 Kitob yuborish")
    )

    keyboard.row(
        types.KeyboardButton("📚 Kitoblar soni"),
        types.KeyboardButton("👥 Foydalanuvchilar soni")
    )

    keyboard.row(
        types.KeyboardButton("🚪 Chiqish")
    )

    return keyboard


# ==========================================
# /START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    # Foydalanuvchini bazaga qo‘shish
    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, first_name)
        VALUES (?, ?)
        """,
        (
            message.from_user.id,
            message.from_user.first_name
        )
    )

    conn.commit()

    bot.send_message(
        message.chat.id,

        "📚 <b>Onlayn Kutubxonaga xush kelibsiz!</b>\n\n"
        "🔎 Kitob qidirish tugmasini bosing.",

        parse_mode="HTML",
        reply_markup=main_keyboard()
    )


# ==========================================
# ⚙️ /ADMIN
# ==========================================

@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:

        bot.send_message(
            message.chat.id,
            "❌ Siz admin emassiz."
        )

        return

    bot.send_message(
        message.chat.id,

        "⚙️ <b>ADMIN PANEL</b>\n\n"
        "Kerakli bo‘limni tanlang:",

        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )


# ==========================================
# 🔎 KITOB QIDIRISH TUGMASI
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "🔎 Kitob qidirish"
)
def search_button(message):

    bot.send_message(
        message.chat.id,

        "🔎 <b>Kitob nomini yozing:</b>\n\n"
        "Masalan:\n"
        "📖 Alpomish\n"
        "📖 O‘tkan kunlar\n"
        "📖 Mehrobdan chayon",

        parse_mode="HTML"
    )


# ==========================================
# 📤 KITOB YUBORISH
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "📤 Kitob yuborish"
)
def add_book(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,

        "📤 <b>KITOB QABUL QILISH REJIMI</b>\n\n"

        "📚 Istagancha kitob yuborishingiz mumkin.\n\n"

        "⚡ 1 ta\n"
        "⚡ 10 ta\n"
        "⚡ 100 ta\n"
        "⚡ 1000 ta kitob\n\n"

        "Kitoblarni ketma-ket yuboring.\n"
        "Bot ularni avtomatik qabul qiladi.\n\n"

        "✅ PDF\n"
        "✅ TXT\n"
        "✅ EPUB",

        parse_mode="HTML",
        reply_markup=admin_keyboard()
    )


# ==========================================
# 📚 KITOBNI QABUL QILISH
# ==========================================

@bot.message_handler(content_types=["document"])
def receive_book(message):

    if message.from_user.id != ADMIN_ID:
        return

    filename = message.document.file_name

    # Faqat PDF, TXT, EPUB
    if not filename.lower().endswith(
        (".pdf", ".txt", ".epub")
    ):
        return

    try:

        # Telegram file_id
        file_id = message.document.file_id

        # Kitob nomi
        book_name = os.path.splitext(
            filename
        )[0]

        # ==================================
        # 📚 BAZAGA SAQLASH
        # ==================================

        cursor.execute(
            """
            INSERT OR IGNORE INTO books
            (name, filename, telegram_file_id)
            VALUES (?, ?, ?)
            """,
            (
                book_name,
                filename,
                file_id
            )
        )

        conn.commit()

        # ==================================
        # 📢 GURUHGA YUBORISH
        # ==================================

        try:

            bot.send_document(
                GROUP_ID,
                file_id,

                caption=(
                    f"📖 <b>{book_name}</b>\n\n"
                    f"📚 Onlayn Kutubxona"
                ),

                parse_mode="HTML"
            )

        except Exception as e:

            print(
                "Guruhga yuborishda xato:",
                e
            )

        # Admin chatiga ortiqcha xabar yuborilmaydi
        print(
            f"✅ Qabul qilindi: {book_name}"
        )

    except Exception as e:

        print(
            f"❌ Kitob qabul qilishda xato: {e}"
        )


# ==========================================
# 📚 KITOBLAR SONI
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "📚 Kitoblar soni"
)
def books_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM books"
    )

    count = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,

        f"📚 <b>Bazadagi kitoblar:</b> {count} ta",

        parse_mode="HTML"
    )


# ==========================================
# 👥 FOYDALANUVCHILAR SONI
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "👥 Foydalanuvchilar soni"
)
def users_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cursor.fetchone()[0]

    bot.send_message(
        message.chat.id,

        f"👥 <b>Foydalanuvchilar soni:</b> {count} ta",

        parse_mode="HTML"
    )


# ==========================================
# 🚪 ADMIN PANELDAN CHIQISH
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "🚪 Chiqish"
)
def exit_admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,

        "🚪 Admin paneldan chiqdingiz.",

        reply_markup=main_keyboard()
    )


# ==========================================
# 🔎 BAZADAN KITOB QIDIRISH
# ==========================================

@bot.message_handler(content_types=["text"])
def search_book(message):

    search_text = message.text.strip()

    if not search_text:
        return

    # Tugmalarni qidiruvga kiritmaslik
    if search_text in [
        "🔎 Kitob qidirish",
        "📤 Kitob yuborish",
        "📚 Kitoblar soni",
        "👥 Foydalanuvchilar soni",
        "🚪 Chiqish"
    ]:
        return

    # ==================================
    # 📚 BAZADAN QIDIRISH
    # ==================================

    cursor.execute(
        """
        SELECT
            name,
            filename,
            telegram_file_id

        FROM books

        WHERE LOWER(name) LIKE ?
        """,
        (
            "%" + search_text.lower() + "%",
        )
    )

    books = cursor.fetchall()

    # ==================================
    # ❌ TOPILMADI
    # ==================================

    if not books:

        bot.send_message(
            message.chat.id,

            "❌ <b>Kitob topilmadi.</b>\n\n"
            "🔎 Kitob nomini boshqacha yozib ko‘ring.",

            parse_mode="HTML"
        )

        return

    # ==================================
    # 📖 KITOB TOPILDI
    # ==================================

    for book in books:

        book_name = book[0]
        file_id = book[2]

        try:

            # 📢 Guruhga yuborish
            bot.send_document(
                GROUP_ID,
                file_id,

                caption=(
                    f"📖 <b>{book_name}</b>\n\n"
                    f"📚 Onlayn Kutubxona"
                ),

                parse_mode="HTML"
            )

            # 👤 Foydalanuvchiga yuborish
            bot.send_document(
                message.chat.id,
                file_id,

                caption=f"📖 <b>{book_name}</b>",

                parse_mode="HTML"
            )

        except Exception as e:

            print(
                "Kitob yuborishda xato:",
                e
            )

            bot.send_message(
                message.chat.id,

                "❌ Kitobni yuborishda xatolik yuz berdi."
            )


# ==========================================
# 🤖 BOTNI ISHGA TUSHIRISH
# ==========================================

print(
    "🤖 Onlayn Kutubxona bot ishga tushdi!"
)

print(
    f"👤 Admin ID: {ADMIN_ID}"
)

print(
    f"📢 Kitob yuboriladigan guruh: {GROUP_ID}"
)

print(
    f"📚 Baza guruhi: {DATABASE_ID}"
)

bot.infinity_polling(
    skip_pending=True
)
