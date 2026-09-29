import sqlite3
import telebot
from telebot import types

# ==========================================
# 🔑 SOZLAMALAR
# ==========================================

TOKEN = "8806238942:AAEhQsLhVHtncIVlvrKjgrBVYUBwKtHMLeU"

ADMIN_ID = 8694801795

# 📢 Kitoblar yuboriladigan asosiy guruh
GROUP_ID = -1003753451546

# 📚 KITOBLAR BAZA KANALI
DATABASE_ID = -1003929551106


bot = telebot.TeleBot(TOKEN)


# ==========================================
# 🗄️ SQLITE DATABASE
# ==========================================

conn = sqlite3.connect(
    "books.db",
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    file_name TEXT,
    file_id TEXT UNIQUE,
    channel_message_id INTEGER
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")


conn.commit()


# ==========================================
# 👤 FOYDALANUVCHINI SAQLASH
# ==========================================

def save_user(user_id):

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )

    conn.commit()


# ==========================================
# 🔐 ADMIN TEKSHIRISH
# ==========================================

def is_admin(user_id):

    return user_id == ADMIN_ID


# ==========================================
# 📊 STATISTIKA
# ==========================================

def get_user_count():

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    return cursor.fetchone()[0]


def get_book_count():

    cursor.execute(
        "SELECT COUNT(*) FROM books"
    )

    return cursor.fetchone()[0]


# ==========================================
# 🚀 START
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    save_user(message.from_user.id)

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🔎 Kitob qidirish",
        "📚 Kitoblar soni"
    )

    bot.send_message(
        message.chat.id,

        """📚 Onlayn Kutubxonaga xush kelibsiz!

🔎 Kitob nomini yozing.
📖 Sizga kerakli kitobni bazadan topib beraman.

Masalan:
📕 O‘tkan kunlar
📘 Mehrobdan chayon
📗 Python""",

        reply_markup=keyboard
    )


# ==========================================
# 🔐 ADMIN PANEL
# ==========================================

@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if not is_admin(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "⛔ Siz admin emassiz."
        )

        return


    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "📥 Kitob qo‘shish",
        "📊 Statistika"
    )

    keyboard.row(
        "❌ Admin paneldan chiqish"
    )


    bot.send_message(
        message.chat.id,

        """🔐 ADMIN PANEL

📥 Kitob qo‘shish
📊 Statistika

Kitob qo‘shish tugmasini bosing va
kitoblarni ketma-ket yuboring.

⚡ 1 ta
⚡ 10 ta
⚡ 100 ta
⚡ 1000 ta

kitobni ketma-ket yuborishingiz mumkin.""",

        reply_markup=keyboard
    )


# ==========================================
# 📥 KITOB QO‘SHISH REJIMI
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.from_user.id == ADMIN_ID
    and message.text == "📥 Kitob qo‘shish"
)
def add_book_mode(message):

    bot.send_message(
        message.chat.id,

        """📥 KITOB QO‘SHISH REJIMI

Endi kitob fayllarini yuboring.

✅ PDF
✅ TXT
✅ EPUB

Kitob yuborilganda avtomatik:

1️⃣ Baza kanaliga yuboriladi
2️⃣ Kitob nomi saqlanadi
3️⃣ Kitob ID'si saqlanadi
4️⃣ Keyinchalik qidirish mumkin bo‘ladi

⚡ Kitoblarni ketma-ket yuboravering.""",
    )


# ==========================================
# 📊 STATISTIKA
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.from_user.id == ADMIN_ID
    and message.text == "📊 Statistika"
)
def statistics(message):

    users = get_user_count()
    books = get_book_count()

    bot.send_message(
        message.chat.id,

        f"""📊 BOT STATISTIKASI

👥 Foydalanuvchilar: {users}

📚 Bazadagi kitoblar: {books}

🗄 Baza kanali:
{DATABASE_ID}"""
    )


# ==========================================
# ❌ ADMIN PANELDAN CHIQISH
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.from_user.id == ADMIN_ID
    and message.text == "❌ Admin paneldan chiqish"
)
def exit_admin(message):

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row(
        "🔎 Kitob qidirish",
        "📚 Kitoblar soni"
    )

    bot.send_message(
        message.chat.id,
        "🏠 Asosiy menyuga qaytdingiz.",
        reply_markup=keyboard
    )


# ==========================================
# 📚 KITOBLAR SONI
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text == "📚 Kitoblar soni"
)
def books_count(message):

    save_user(message.from_user.id)

    count = get_book_count()

    bot.send_message(
        message.chat.id,

        f"📚 Kutubxonada hozir {count} ta kitob mavjud."
    )


# ==========================================
# 📥 KITOB QABUL QILISH
# ==========================================

@bot.message_handler(
    content_types=["document"]
)
def receive_book(message):

    # Faqat admin kitob qo‘sha oladi
    if not is_admin(message.from_user.id):

        bot.send_message(
            message.chat.id,
            "⛔ Kitob qo‘shish faqat admin uchun."
        )

        return


    document = message.document

    file_name = document.file_name

    file_id = document.file_id


    # ======================================
    # 📄 FORMAT TEKSHIRISH
    # ======================================

    allowed = (
        file_name.lower().endswith(".pdf")
        or file_name.lower().endswith(".txt")
        or file_name.lower().endswith(".epub")
    )


    if not allowed:

        bot.send_message(
            message.chat.id,

            "❌ Noto‘g‘ri format.\n\n"
            "Faqat PDF, TXT yoki EPUB yuboring."
        )

        return


    # ======================================
    # 📚 KITOB NOMI
    # ======================================

    book_name = file_name.rsplit(
        ".",
        1
    )[0]


    # ======================================
    # 🗄 BAZA KANALIGA YUBORISH
    # ======================================

    channel_message_id = None

    try:

        sent_message = bot.send_document(
            DATABASE_ID,
            file_id,

            caption=f"""📚 {book_name}

🔎 Qidiruv uchun:
{book_name}"""
        )

        channel_message_id = sent_message.message_id


    except Exception as e:

        print(
            "❌ Baza kanaliga yuborishda xato:",
            e
        )

        bot.send_message(
            message.chat.id,

            """⚠️ Kitob baza kanaliga yuborilmadi.

Botni baza kanaliga administrator qilib
qo‘shganingizni tekshiring."""
        )

        return


    # ======================================
    # 🗄 SQLITE GA SAQLASH
    # ======================================

    try:

        cursor.execute(
            """
            INSERT OR IGNORE INTO books
            (
                name,
                file_name,
                file_id,
                channel_message_id
            )
            VALUES (?, ?, ?, ?)
            """,

            (
                book_name,
                file_name,
                file_id,
                channel_message_id
            )
        )

        conn.commit()


    except Exception as e:

        print(
            "Database error:",
            e
        )


    # ======================================
    # 📢 ASOSIY GURUHGA YUBORISH
    # ======================================

    try:

        bot.send_document(
            GROUP_ID,
            file_id,

            caption=f"📚 {book_name}"
        )

    except Exception as e:

        print(
            "Guruhga yuborishda xato:",
            e
        )


    # ======================================
    # ✅ ADMIN XABARI
    # ======================================

    bot.send_message(
        message.chat.id,

        f"""✅ KITOB QABUL QILINDI

📚 Nomi:
{book_name}

🗄 Baza kanaliga saqlandi.

🆔 Kanal xabar ID:
{channel_message_id}

⚡ Keyingi kitobni yuborishingiz mumkin."""
    )


# ==========================================
# 🔎 KITOB QIDIRISH
# ==========================================

@bot.message_handler(
    func=lambda message:
    message.text
    and not message.text.startswith("/")
    and message.text not in [
        "🔎 Kitob qidirish",
        "📚 Kitoblar soni",
        "📥 Kitob qo‘shish",
        "📊 Statistika",
        "❌ Admin paneldan chiqish"
    ]
)
def search_book(message):

    save_user(message.from_user.id)

    search_text = message.text.strip()


    # ======================================
    # 🔎 SQLITE BAZADAN QIDIRISH
    # ======================================

    cursor.execute(
        """
        SELECT
            name,
            file_name,
            file_id,
            channel_message_id
        FROM books

        WHERE name LIKE ?

        LIMIT 10
        """,

        (
            f"%{search_text}%",
        )
    )


    results = cursor.fetchall()


    # ======================================
    # ❌ TOPILMADI
    # ======================================

    if not results:

        bot.send_message(
            message.chat.id,

            f"""❌ Kitob topilmadi.

🔎 Qidirilgan:
{search_text}

Boshqa nom bilan qayta urinib ko‘ring."""
        )

        return


    # ======================================
    # 📚 NATIJALAR
    # ======================================

    bot.send_message(
        message.chat.id,

        f"""🔎 Qidiruv natijasi

📚 {len(results)} ta kitob topildi."""
    )


    for name, file_name, file_id, channel_message_id in results:

        try:

            bot.send_document(
                message.chat.id,

                file_id,

                caption=f"""📚 {name}

📄 {file_name}"""
            )


        except Exception as e:

            print(
                "Kitob yuborishda xato:",
                e
            )


# ==========================================
# ▶️ BOTNI ISHGA TUSHIRISH
# ==========================================

print(
    "🤖 Onlayn Kutubxona bot ishga tushdi..."
)

bot.infinity_polling()
