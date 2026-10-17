import sqlite3
import hashlib
import re
import io
import os
import aiohttp
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops, ImageStat
import pytesseract
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                       KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler, filters, ContextTypes)

# ── Tesseract path (Windows) ──────────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

TOKEN = "8612836179:AAEw365hOqEsDrx1cbpdyqOOsrgToY1fz9s"
ADMIN_ID = 7091106384
ADMIN_ID2 = 7775597088
DB_FILE = "mezzo.db"

# ── Cashbox API config (fill in your real credentials here, never share them) ──
CASHBOX_URL      = "https://cashbox.mezzo.bet"
CASHBOX_USERNAME = "YOUR_USERNAME_HERE"   # e.g. "AselaAdig35-1"
CASHBOX_PASSWORD = "YOUR_PASSWORD_HERE"   # e.g. "66134635"

# ── Cashbox: fetch live balance by Mezzo ID ───────────────────────────────────

async def cashbox_get_balance(mezzo_id: str) -> str | None:
    """
    Log in to cashbox.mezzo.bet, look up the user by Mezzo ID,
    and return their balance as a string (e.g. "1,250.00").
    Returns None on any error.
    """
    # Common endpoint patterns — tries multiple in order
    login_endpoints = [
        f"{CASHBOX_URL}/api/auth/login",
        f"{CASHBOX_URL}/api/login",
        f"{CASHBOX_URL}/auth/login",
        f"{CASHBOX_URL}/signin",
    ]
    balance_endpoints = [
        f"{CASHBOX_URL}/api/users/balance",
        f"{CASHBOX_URL}/api/balance",
        f"{CASHBOX_URL}/api/user/balance",
        f"{CASHBOX_URL}/api/account/balance",
    ]

    try:
        async with aiohttp.ClientSession() as session:

            # ── Step 1: try each login endpoint until one works ────────────
            token = None
            for login_url in login_endpoints:
                try:
                    login_resp = await session.post(
                        login_url,
                        json={"username": CASHBOX_USERNAME, "password": CASHBOX_PASSWORD},
                        timeout=aiohttp.ClientTimeout(total=10)
                    )
                    if login_resp.status == 200:
                        login_data = await login_resp.json()
                        token = (
                            login_data.get("token") or
                            login_data.get("access_token") or
                            login_data.get("data", {}).get("token") or
                            login_data.get("result", {}).get("token")
                        )
                        if token:
                            break
                except Exception:
                    continue

            if not token:
                return None

            # ── Step 2: try each balance endpoint ─────────────────────────
            headers = {"Authorization": f"Bearer {token}"}
            for balance_url in balance_endpoints:
                try:
                    bal_resp = await session.get(
                        balance_url,
                        params={"mezzo_id": mezzo_id, "id": mezzo_id, "username": mezzo_id},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    )
                    if bal_resp.status == 200:
                        bal_data = await bal_resp.json()
                        balance = (
                            bal_data.get("balance") or
                            bal_data.get("amount") or
                            bal_data.get("data", {}).get("balance") or
                            bal_data.get("result", {}).get("balance")
                        )
                        if balance is not None:
                            return str(balance)
                except Exception:
                    continue

            return None

    except Exception:
        return None

# ── TX ID Validation (from tx_verification_module) ────────────────────────────

def init_tx_table(cur):
    """Create transaction_ids table (called inside init_db)."""
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transaction_ids (
            tx_id      TEXT PRIMARY KEY,
            user_id    INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

def is_tx_used(tx_id: str) -> bool:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM transaction_ids WHERE tx_id = ?", (tx_id,))
    found = cur.fetchone() is not None
    con.close()
    return found

def save_tx(tx_id: str, user_id: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO transaction_ids (tx_id, user_id) VALUES (?, ?)",
        (tx_id, user_id)
    )
    con.commit()
    con.close()

def extract_tx_id(text: str):
    """
    Extract transaction ID from raw text (OCR or receipt link page).
    Returns (tx_id, source) or (None, None).
    """
    upper = text.upper()
    # CBE format: FT + 8-12 digits
    cbe = re.search(r'\bFT\d{8,12}\b', upper)
    # Telebirr format: 2-4 letters + 6-10 digits
    telebirr = re.search(r'\b[A-Z]{2,4}\d{6,10}\b', upper)
    # Generic alphanumeric 8-14 chars (must have both letters and digits)
    generic = re.search(
        r'\b(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*\d)[A-Z0-9]{8,14}\b', upper
    )
    if cbe:
        return cbe.group(), "CBE"
    elif telebirr:
        return telebirr.group(), "TELEBIRR"
    elif generic:
        return generic.group(), "UNKNOWN"
    return None, None

def extract_tx_from_link(url: str) -> str | None:
    """Try to pull a TX ID directly from a receipt URL query string."""
    match = re.search(r'(?:trxid|txid|ref|id)[=:/\-]?([A-Za-z0-9]{6,})', url, re.I)
    return match.group(1).upper() if match else None

def is_valid_tx(tx_id: str) -> bool:
    """Basic sanity check: ≥8 chars, contains both letters and digits."""
    if not tx_id or len(tx_id) < 8:
        return False
    if not any(c.isdigit() for c in tx_id):
        return False
    if not any(c.isalpha() for c in tx_id):
        return False
    return True

# ── Image Tamper Detection ────────────────────────────────────────────────────

def detect_image_tampering(img) -> bool:
    """
    Detect possible edited/photoshopped regions using pixel inconsistency.
    Compares the image against a blurred version of itself — high variance
    in the difference means the image likely has sharp artificial edits.
    Returns True if the image looks suspicious.
    """
    grayscale = img.convert("L")
    diff = ImageChops.difference(grayscale, grayscale.filter(ImageFilter.GaussianBlur(3)))
    stat = ImageStat.Stat(diff)
    variance = sum(stat.var) / len(stat.var)
    return variance > 500  # threshold — higher = more suspicious

def detect_text_anomalies(ocr_text: str) -> bool:
    """
    Analyse OCR text for signs of a fake or edited receipt.
    Scores 3 red flags — returns True (suspicious) if 2+ are triggered:
      1. Missing success keywords (SUCCESS / COMPLETED)
      2. Unusual symbols common in edited images
      3. Too few words (broken/sparse text)
    """
    score = 0
    if "SUCCESS" not in ocr_text and "COMPLETED" not in ocr_text:
        score += 1
    if re.search(r'[^\w\s:.\-]', ocr_text):
        score += 1
    if len(ocr_text.split()) < 5:
        score += 1
    return score >= 2

# ── Database ──────────────────────────────────────────────────────────────────

def init_db():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY,
            name      TEXT,
            phone     TEXT,
            mezzo_id  TEXT,
            balance   INTEGER DEFAULT 0
        )
    """)
    try:
        cur.execute("ALTER TABLE users ADD COLUMN mezzo_id TEXT")
    except Exception:
        pass
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            type       TEXT,
            amount     INTEGER,
            note       TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receipt_links (
            link     TEXT PRIMARY KEY,
            user_id  INTEGER,
            used_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Stores pending requests waiting for admin decision
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_requests (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            type       TEXT,
            amount     INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            user_id    INTEGER PRIMARY KEY,
            name       TEXT,
            added_by   INTEGER,
            added_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Transaction ID dedup table
    init_tx_table(cur)

    # Always make sure the super admin is in the table
    cur.execute("""
        INSERT OR IGNORE INTO admins (user_id, name, added_by)
        VALUES (?, 'Super Admin', ?)
    """, (ADMIN_ID, ADMIN_ID))
    # Second admin
    cur.execute("""
        INSERT OR IGNORE INTO admins (user_id, name, added_by)
        VALUES (?, 'Admin 2', ?)
    """, (ADMIN_ID2, ADMIN_ID))
    con.commit()
    con.close()

def is_link_used(link: str) -> bool:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM receipt_links WHERE link = ?", (link,))
    found = cur.fetchone() is not None
    con.close()
    return found

def mark_link_used(link: str, user_id: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO receipt_links (link, user_id) VALUES (?, ?)", (link, user_id))
    con.commit()
    con.close()

def get_user(user_id: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT user_id, name, phone, mezzo_id, balance FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    con.close()
    if row:
        return {"user_id": row[0], "name": row[1], "phone": row[2], "mezzo_id": row[3], "balance": row[4]}
    return None

def save_user(user_id: int, name: str, phone: str):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO users (user_id, name, phone, mezzo_id, balance)
        VALUES (?, ?, ?, NULL, 0)
        ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, phone=excluded.phone
    """, (user_id, name, phone))
    con.commit()
    con.close()

def save_mezzo_id(user_id: int, mezzo_id: str):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET mezzo_id = ? WHERE user_id = ?", (mezzo_id, user_id))
    con.commit()
    con.close()

def get_balance(user_id: int) -> int:
    user = get_user(user_id)
    return user["balance"] if user else 0

def add_balance(user_id: int, amount: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    cur.execute(
        "INSERT INTO transactions (user_id, type, amount, note) VALUES (?, 'deposit', ?, 'Admin confirmed')",
        (user_id, amount)
    )
    con.commit()
    con.close()

def remove_balance(user_id: int, amount: int) -> bool:
    """Deduct balance. Returns False if user doesn't have enough."""
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row or row[0] < amount:
        con.close()
        return False
    cur.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
    cur.execute(
        "INSERT INTO transactions (user_id, type, amount, note) VALUES (?, 'withdraw', ?, 'Admin deducted')",
        (user_id, amount)
    )
    con.commit()
    con.close()
    return True

def save_pending(user_id: int, req_type: str, amount: int = 0) -> int:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO pending_requests (user_id, type, amount) VALUES (?, ?, ?)",
        (user_id, req_type, amount)
    )
    req_id = cur.lastrowid
    con.commit()
    con.close()
    return req_id

def get_pending(req_id: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT id, user_id, type, amount FROM pending_requests WHERE id = ?", (req_id,))
    row = cur.fetchone()
    con.close()
    if row:
        return {"id": row[0], "user_id": row[1], "type": row[2], "amount": row[3]}
    return None

def get_all_pending():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        SELECT p.id, p.user_id, p.type, p.amount, p.created_at,
               u.name, u.mezzo_id, u.phone
        FROM pending_requests p
        LEFT JOIN users u ON p.user_id = u.user_id
        ORDER BY p.created_at ASC
    """)
    rows = cur.fetchall()
    con.close()
    return rows

def delete_pending(req_id: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("DELETE FROM pending_requests WHERE id = ?", (req_id,))
    con.commit()
    con.close()

def is_admin(user_id: int) -> bool:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
    found = cur.fetchone() is not None
    con.close()
    return found

def is_super_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def add_admin(user_id: int, name: str, added_by: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO admins (user_id, name, added_by) VALUES (?, ?, ?)",
        (user_id, name, added_by)
    )
    con.commit()
    con.close()

def remove_admin(user_id: int):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    con.commit()
    con.close()

def get_all_admins():
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT user_id, name, added_at FROM admins ORDER BY added_at")
    rows = cur.fetchall()
    con.close()
    return rows

def get_all_user_ids() -> list:
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("SELECT user_id FROM users WHERE mezzo_id IS NOT NULL")
    rows = cur.fetchall()
    con.close()
    return [row[0] for row in rows]

def get_transactions(user_id: int, limit: int = 10):
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    cur.execute("""
        SELECT type, amount, note, created_at FROM transactions
        WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    con.close()
    return rows

# ── Helpers ───────────────────────────────────────────────────────────────────

def is_receipt_link(text: str) -> bool:
    return "apps.cbe.com.et" in text or "transactioninfo.ethiotelecom.et" in text

def get_bottom_menu():
    """Persistent bottom reply keyboard shown at all times."""
    keyboard = [
        ["🏠 Home", "💰 Balance"],
        ["➕ Deposit", "➖ Withdraw"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, persistent=True)

async def notify_all_admins(context, text: str, reply_markup=None):
    """Send a message to all admins."""
    for admin in get_all_admins():
        try:
            await context.bot.send_message(
                chat_id=admin[0],
                text=text,
                reply_markup=reply_markup
            )
        except Exception:
            pass

async def forward_to_all_admins(context, from_chat_id: int, message_id: int):
    """Forward a message to all admins."""
    for admin in get_all_admins():
        try:
            await context.bot.forward_message(
                chat_id=admin[0],
                from_chat_id=from_chat_id,
                message_id=message_id
            )
        except Exception:
            pass

def admin_buttons(req_id: int, req_type: str):
    """Returns ✅ Accept / ❌ Decline inline keyboard for admin."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Accept", callback_data=f"admin_accept_{req_type}_{req_id}"),
        InlineKeyboardButton("❌ Decline", callback_data=f"admin_decline_{req_type}_{req_id}")
    ]])

# ── User handlers ─────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = get_user(user_id)
    if db_user and db_user.get("phone") and db_user.get("mezzo_id"):
        await show_main_menu(update, context)
        return
    elif db_user and db_user.get("phone"):
        context.user_data.clear()
        context.user_data["waiting_mezzo_id"] = True
        await update.message.reply_text(
            "👋 Welcome back to Mezzo Bot!\n\nPlease enter your mezzo.bet ID to complete registration:",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    keyboard = [[KeyboardButton("📱 Share Phone Number", request_contact=True)]]
    await update.message.reply_text(
        "👋 Welcome to Mezzo Bot!\n\nPlease share your phone number to continue.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def receive_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    phone = update.message.contact.phone_number
    save_user(user.id, user.first_name, phone)
    context.user_data.clear()
    context.user_data["waiting_mezzo_id"] = True
    await update.message.reply_text(
        "✅ Phone number received!\n\n"
        "Please enter your mezzo.bet ID:",
        reply_markup=ReplyKeyboardRemove()
    )

async def show_main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("🌐 Open Website", url="https://mezzo.bet")],
        [InlineKeyboardButton("➕ Deposit", callback_data="deposit"),
         InlineKeyboardButton("➖ Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("💰 Balance", callback_data="balance"),
         InlineKeyboardButton("🆘 Support", callback_data="support")],
        [InlineKeyboardButton("📋 Transactions", callback_data="transactions")]
    ]
    await update.message.reply_text(
        "📌 Main Menu\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    # Attach persistent bottom keyboard
    await update.message.reply_text(
        "Use the buttons below for quick access:",
        reply_markup=get_bottom_menu()
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# ── Button handler ────────────────────────────────────────────────────────────

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    # ── Admin: Accept or Decline ───────────────────────────────────────────
    if data.startswith("admin_accept_") or data.startswith("admin_decline_"):
        if not is_admin(user_id):
            await query.answer("⛔ Admin only.", show_alert=True)
            return

        parts = data.split("_")
        # format: admin_accept_deposit_<req_id>  or  admin_decline_withdraw_<req_id>
        action   = parts[1]          # accept / decline
        req_type = parts[2]          # deposit / withdraw
        req_id   = int(parts[3])

        req = get_pending(req_id)
        if not req:
            await query.edit_message_reply_markup(reply_markup=None)
            await query.message.reply_text("⚠️ This request was already handled.")
            return

        target_user = get_user(req["user_id"])
        name = target_user["name"] if target_user else "User"
        delete_pending(req_id)

        if action == "accept":
            if req_type == "deposit":
                amount = req["amount"]
                add_balance(req["user_id"], amount)
                # Notify user
                await context.bot.send_message(
                    chat_id=req["user_id"],
                    text=(
                        f"✅ Deposit Confirmed!\n"
                        f"Amount: {amount} ETB has been added to your balance.\n"
                        f"Thank you! 🎉"
                    )
                )
                # Update admin message
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(
                    f"✅ Accepted deposit of {amount} ETB for {name}."
                )
            else:  # withdraw
                await context.bot.send_message(
                    chat_id=req["user_id"],
                    text=(
                        "✅ Withdraw Approved!\n"
                        "Your withdrawal is being processed.\n"
                        "You will receive your funds shortly. 🎉"
                    )
                )
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(
                    f"✅ Accepted withdrawal request for {name}."
                )
        else:  # decline
            if req_type == "deposit":
                await context.bot.send_message(
                    chat_id=req["user_id"],
                    text=(
                        "❌ Deposit Declined.\n\n"
                        "Your payment could not be verified.\n"
                        "Please contact support: @mezzodeposite"
                    )
                )
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(
                    f"❌ Declined deposit request for {name}."
                )
            else:  # withdraw
                await context.bot.send_message(
                    chat_id=req["user_id"],
                    text=(
                        "❌ Withdrawal Declined.\n\n"
                        "Your withdrawal could not be processed.\n"
                        "Please contact support: @mezzodeposite"
                    )
                )
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(
                    f"❌ Declined withdrawal request for {name}."
                )
        return

    # ── User menu buttons ──────────────────────────────────────────────────
    if data == "deposit":
        keyboard = [
            [InlineKeyboardButton("50",   callback_data="amt_50"),
             InlineKeyboardButton("100",  callback_data="amt_100")],
            [InlineKeyboardButton("200",  callback_data="amt_200"),
             InlineKeyboardButton("500",  callback_data="amt_500")],
            [InlineKeyboardButton("1000", callback_data="amt_1000"),
             InlineKeyboardButton("2000", callback_data="amt_2000")],
            [InlineKeyboardButton("✏️ Custom", callback_data="amt_custom")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await query.edit_message_text(
            "💰 Select deposit amount (ETB):\n\n⚠️ Minimum deposit: 50 ETB",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("amt_"):
        amount = data.replace("amt_", "")
        if amount == "custom":
            context.user_data["waiting_custom"] = True
            await query.edit_message_text("✏️ Type your custom amount and send it:")
            return
        context.user_data["deposit_amount"] = amount
        context.user_data["waiting_custom"] = False
        keyboard = [
            [InlineKeyboardButton("📱 Telebirr", callback_data="pay_telebirr")],
            [InlineKeyboardButton("🏦 CBE Bank", callback_data="pay_cbe")],
            [InlineKeyboardButton("🔙 Back", callback_data="deposit")]
        ]
        await query.edit_message_text(
            f"💳 Amount: {amount} ETB\n\nChoose payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "pay_telebirr":
        amount = context.user_data.get("deposit_amount", "?")
        await query.edit_message_text(
            f"📱 TELEBIRR PAYMENT\n\n"
            f"Amount: {amount} ETB\n"
            f"Send to: 0910534013\n\n"
            f"After paying:\n"
            f"📸 Send your screenshot here\n"
            f"We confirm within 5 min ✅",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="deposit")]])
        )

    elif data == "pay_cbe":
        amount = context.user_data.get("deposit_amount", "?")
        await query.edit_message_text(
            f"🏦 CBE PAYMENT\n\n"
            f"Amount: {amount} ETB\n"
            f"Account: 1000661082902\n"
            f"Name: Your Name\n\n"
            f"📸 Send your screenshot here\n"
            f"We confirm within 5 min ✅",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="deposit")]])
        )

    elif data == "balance":
        user_row = get_user(user_id)
        mezzo_id = user_row["mezzo_id"] if user_row else None

        if mezzo_id:
            await query.edit_message_text("⏳ Fetching your live balance...")
            live_balance = await cashbox_get_balance(mezzo_id)
            if live_balance is not None:
                balance_text = f"💰 YOUR BALANCE\n\n🌐 Live (mezzo.bet): {live_balance} ETB"
            else:
                # Fallback to local DB if cashbox API fails
                local_bal = get_balance(user_id)
                balance_text = (
                    f"💰 YOUR BALANCE\n\n"
                    f"Available: {local_bal} ETB\n"
                    f"⚠️ Balance service is temporarily unavailable.\n"
                    f"Contact support: @mezzodeposite"
                )
        else:
            local_bal = get_balance(user_id)
            balance_text = (
                f"💰 YOUR BALANCE\n\n"
                f"Available: {local_bal} ETB\n"
                f"⚠️ No Mezzo ID linked to your account."
            )

        await query.edit_message_text(
            balance_text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )

    elif data == "withdraw":
        context.user_data["waiting_withdraw_code"] = True
        await query.edit_message_text(
            "➖ WITHDRAW\n\n"
            "⚠️ Minimum withdrawal: 500 ETB\n\n"
            "mezzo.bet ላይ withdraw ካዘዛቹ በኋላ የሚሰጣቹን code ላኩልን 📸",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )

    elif data == "support":
        await query.edit_message_text(
            "🆘 SUPPORT\n\n"
            "Contact us:\n"
            "Telegram: @mezzodeposite\n"
            "Phone: +251712759695\n"
            "Hours: 12AM - 12PM",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )

    elif data == "transactions":
        rows = get_transactions(user_id)
        if rows:
            lines = []
            for t_type, amount, note, created_at in rows:
                emoji = "➕" if t_type == "deposit" else "➖"
                lines.append(f"{emoji} {amount} ETB — {note}\n🕐 {created_at[:16]}")
            text = "📋 TRANSACTIONS\n\n" + "\n\n".join(lines)
        else:
            text = "📋 TRANSACTIONS\n\nNo transactions yet."
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back")]])
        )

    elif data == "back":
        context.user_data["waiting_withdraw_code"] = False
        keyboard = [
            [InlineKeyboardButton("🌐 Open Website", url="https://mezzo.bet")],
            [InlineKeyboardButton("➕ Deposit", callback_data="deposit"),
             InlineKeyboardButton("➖ Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("💰 Balance", callback_data="balance"),
             InlineKeyboardButton("🆘 Support", callback_data="support")],
            [InlineKeyboardButton("📋 Transactions", callback_data="transactions")]
        ]
        await query.edit_message_text(
            "📌 Main Menu\nChoose an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ── Text handler ──────────────────────────────────────────────────────────────

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.message.from_user

    # ── Bottom menu button taps ────────────────────────────────────────────
    if text == "🏠 Home":
        await show_main_menu(update, context)
        return
    if text == "💰 Balance":
        user_row = get_user(user.id)
        mezzo_id = user_row["mezzo_id"] if user_row else None
        if mezzo_id:
            await update.message.reply_text("⏳ Fetching your live balance...")
            live_balance = await cashbox_get_balance(mezzo_id)
            if live_balance is not None:
                balance_text = f"💰 YOUR BALANCE\n\n🌐 Live (mezzo.bet): {live_balance} ETB"
            else:
                local_bal = get_balance(user.id)
                balance_text = (
                    f"💰 YOUR BALANCE\n\n"
                    f"Available: {local_bal} ETB\n"
                    f"⚠️ Balance service is temporarily unavailable.\n"
                    f"Contact support: @mezzodeposite"
                )
        else:
            local_bal = get_balance(user.id)
            balance_text = f"💰 YOUR BALANCE\n\nAvailable: {local_bal} ETB"
        await update.message.reply_text(balance_text, reply_markup=get_bottom_menu())
        return
    if text == "➕ Deposit":
        keyboard = [
            [InlineKeyboardButton("50",   callback_data="amt_50"),
             InlineKeyboardButton("100",  callback_data="amt_100")],
            [InlineKeyboardButton("200",  callback_data="amt_200"),
             InlineKeyboardButton("500",  callback_data="amt_500")],
            [InlineKeyboardButton("1000", callback_data="amt_1000"),
             InlineKeyboardButton("2000", callback_data="amt_2000")],
            [InlineKeyboardButton("✏️ Custom", callback_data="amt_custom")],
            [InlineKeyboardButton("🔙 Back", callback_data="back")]
        ]
        await update.message.reply_text(
            "💰 Select deposit amount (ETB):\n\n⚠️ Minimum deposit: 50 ETB",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    if text == "➖ Withdraw":
        context.user_data["waiting_withdraw_code"] = True
        await update.message.reply_text(
            "➖ WITHDRAW\n\n"
            "⚠️ Minimum withdrawal: 500 ETB\n\n"
            "mezzo.bet ላይ withdraw ካዘዛቹ በኋላ የሚሰጣቹን code ላኩልን 📸",
            reply_markup=get_bottom_menu()
        )
        return

    # ── Admin broadcast ────────────────────────────────────────────────────
    if is_admin(user.id) and context.user_data.get("waiting_broadcast"):
        context.user_data["waiting_broadcast"] = False
        user_ids = get_all_user_ids()
        sent = 0
        failed = 0
        await update.message.reply_text(f"📤 Sending to {len(user_ids)} users...")
        for uid in user_ids:
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=f"📣 Message from Mezzo Bot:\n\n{text}"
                )
                sent += 1
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ Broadcast complete!\n"
            f"• Sent: {sent}\n"
            f"• Failed: {failed}"
        )
        return

    # ── Registration step 2: mezzo.bet ID ─────────────────────────────────
    db_user = get_user(user.id)
    needs_mezzo_id = (
        context.user_data.get("waiting_mezzo_id") or
        (db_user and not db_user.get("mezzo_id"))
    )

    if needs_mezzo_id and not is_receipt_link(text):
        if not text:
            await update.message.reply_text("⚠️ Please enter your mezzo.bet ID:")
            return
        save_mezzo_id(user.id, text)
        context.user_data["waiting_mezzo_id"] = False
        db_user = get_user(user.id)
        await notify_all_admins(
            context,
            f"🆕 New Registration!\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username}\n"
            f"Telegram ID: {user.id}\n"
            f"Phone: {db_user['phone']}\n"
            f"Mezzo ID: {text}"
        )
        await update.message.reply_text(
            f"✅ Registration complete!\n\n"
            f"📋 Your details:\n"
            f"• Phone: {db_user['phone']}\n"
            f"• Mezzo ID: {text}\n\n"
            f"Welcome to Mezzo Bot! 🎉"
        )
        await show_main_menu(update, context)
        return

    # ── Receipt link ───────────────────────────────────────────────────────
    if is_receipt_link(text):
        db_user  = get_user(user.id)
        phone    = db_user["phone"]    if db_user else "Unknown"
        mezzo_id = db_user["mezzo_id"] if db_user else "Unknown"
        bank     = "🏦 CBE Bank" if "apps.cbe.com.et" in text else "📱 Telebirr"

        # ── Step 1: duplicate link check ──────────────────────────────────
        if is_link_used(text):
            await update.message.reply_text(
                "❌ This receipt link was already submitted.\n\n"
                "If you think this is a mistake, contact support:\n"
                "@mezzodeposite"
            )
            return

        # ── Step 2: extract & validate TX ID from the URL itself ──────────
        tx_id_from_url = extract_tx_from_link(text)
        if tx_id_from_url:
            tx_id = tx_id_from_url
        else:
            # Fallback: try to parse it from the URL path/query generically
            tx_id, _ = extract_tx_id(text)

        # ── Step 3: duplicate TX ID check ─────────────────────────────────
        if tx_id and is_valid_tx(tx_id):
            if is_tx_used(tx_id):
                await update.message.reply_text(
                    f"❌ Duplicate Transaction Detected!\n\n"
                    f"Transaction ID `{tx_id}` has already been used.\n\n"
                    f"If you believe this is an error, contact support:\n"
                    f"@mezzodeposite",
                    parse_mode="Markdown"
                )
                return
            # Mark both the link URL and the TX ID as used
            mark_link_used(text, user.id)
            save_tx(tx_id, user.id)
            tx_display = tx_id
        else:
            # TX ID not found in URL — mark only the link; admin will verify
            mark_link_used(text, user.id)
            tx_display = "Not parsed from URL (admin will verify)"

        # ── Step 4: save pending and notify admins ─────────────────────────
        req_id = save_pending(user.id, "deposit", 0)

        await notify_all_admins(
            context,
            f"🔗 New Receipt Link!\n"
            f"Bank: {bank}\n"
            f"From: {user.first_name}\n"
            f"Username: @{user.username}\n"
            f"Telegram ID: {user.id}\n"
            f"Phone: {phone}\n"
            f"Mezzo ID: {mezzo_id}\n"
            f"TX ID: {tx_display}\n\n"
            f"Link: {text}",
            reply_markup=admin_buttons(req_id, "deposit")
        )
        await update.message.reply_text(
            "✅ Receipt link received! We will verify and confirm within 5 min."
        )
        return

    # ── Custom deposit amount ──────────────────────────────────────────────
    if context.user_data.get("waiting_custom"):
        if not text.isdigit() or int(text) < 50:
            await update.message.reply_text("⚠️ Please enter a valid amount (minimum 50 ETB):")
            return
        context.user_data["deposit_amount"] = text
        context.user_data["waiting_custom"] = False
        keyboard = [
            [InlineKeyboardButton("📱 Telebirr", callback_data="pay_telebirr")],
            [InlineKeyboardButton("🏦 CBE Bank", callback_data="pay_cbe")],
            [InlineKeyboardButton("🔙 Back", callback_data="deposit")]
        ]
        await update.message.reply_text(
            f"💳 Amount: {text} ETB\n\nChoose payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ── Screenshot handler ────────────────────────────────────────────────────────

async def receive_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    # ── Admin broadcast with photo ─────────────────────────────────────────
    if is_admin(user.id) and context.user_data.get("waiting_broadcast"):
        context.user_data["waiting_broadcast"] = False
        caption = update.message.caption or ""
        photo = update.message.photo[-1].file_id
        user_ids = get_all_user_ids()
        sent = 0
        failed = 0
        await update.message.reply_text(f"📤 Sending to {len(user_ids)} users...")
        for uid in user_ids:
            try:
                await context.bot.send_photo(
                    chat_id=uid,
                    photo=photo,
                    caption=f"📣 Message from Mezzo Bot:\n\n{caption}" if caption else "📣 Message from Mezzo Bot"
                )
                sent += 1
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ Broadcast complete!\n"
            f"• Sent: {sent}\n"
            f"• Failed: {failed}"
        )
        return

    db_user  = get_user(user.id)
    phone    = db_user["phone"]    if db_user else "Unknown"
    mezzo_id = db_user["mezzo_id"] if db_user else "Unknown"

    # Download photo bytes
    photo       = update.message.photo[-1]
    photo_file  = await context.bot.get_file(photo.file_id)
    photo_bytes = await photo_file.download_as_bytearray()

    # ── OCR: extract transaction ID and amount ────────────────────────────
    tx_id = None
    ocr_amount = None

    def run_ocr(pil_img):
        combined = ""
        for cfg in ["--psm 6", "--psm 4", "--psm 11"]:
            try:
                combined += " " + pytesseract.image_to_string(pil_img, config=cfg)
            except Exception:
                pass
        return combined.upper()

    try:
        img = Image.open(io.BytesIO(bytes(photo_bytes)))
        w, h = img.size

        # ── Tamper detection ──────────────────────────────────────────────
        is_tampered = detect_image_tampering(img)

        # Attempt 1: grayscale + high contrast
        img_gray = img.convert("L").resize((w * 3, h * 3), Image.LANCZOS)
        img_gray = ImageEnhance.Contrast(img_gray).enhance(3.0)
        img_gray = ImageEnhance.Sharpness(img_gray).enhance(2.5)
        img_gray = img_gray.filter(ImageFilter.MedianFilter(size=3))
        ocr_text = run_ocr(img_gray)

        # Attempt 2: inverted image
        img_inv = ImageOps.invert(img_gray)
        ocr_text += " " + run_ocr(img_inv)

        # Attempt 3: plain upscale no processing
        img_plain = img.convert("L").resize((w * 2, h * 2), Image.LANCZOS)
        ocr_text += " " + run_ocr(img_plain)

        # ── Text anomaly detection ────────────────────────────────────────
        if detect_text_anomalies(ocr_text):
            is_tampered = True  # escalate if text also looks fake

        # Extract Transaction ID
        cbe_match = re.search(r'\bFT\d{8,12}\b', ocr_text)
        telebirr_match = re.search(r'\b(?=[A-Z0-9]*[A-Z])(?=[A-Z0-9]*[0-9])[A-Z0-9]{8,12}\b', ocr_text)

        if cbe_match:
            tx_id = cbe_match.group()
        elif telebirr_match:
            tx_id = telebirr_match.group()

        # Extract Amount (e.g. -51.00, 500, 1,000.00)
        amount_match = re.search(r'-?(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)\s*(?:ETB|BIRR)?', ocr_text)
        if amount_match:
            raw = amount_match.group(1).replace(",", "")
            try:
                ocr_amount = str(int(float(raw)))
            except Exception:
                ocr_amount = None

    except Exception as e:
        tx_id = None
        ocr_amount = None
        is_tampered = False

    if tx_id:
        # ── Validate format ────────────────────────────────────────────────
        if not is_valid_tx(tx_id):
            tx_id = None  # treat as unreadable, fall through to hash check
        else:
            # ── Duplicate TX ID check (covers both link & screenshot paths) ──
            if is_tx_used(tx_id):
                await update.message.reply_text(
                    f"❌ This transaction was already used.\n\n"
                    f"Transaction ID: `{tx_id}`\n\n"
                    f"If you think this is a mistake, contact support:\n"
                    f"@mezzodeposite",
                    parse_mode="Markdown"
                )
                return
            # Also check legacy receipt_links table for the txid: prefix
            if is_link_used(f"txid:{tx_id}"):
                await update.message.reply_text(
                    f"❌ This transaction was already used.\n\n"
                    f"Transaction ID: `{tx_id}`\n\n"
                    f"If you think this is a mistake, contact support:\n"
                    f"@mezzodeposite",
                    parse_mode="Markdown"
                )
                return
            # Mark in both tables
            save_tx(tx_id, user.id)
            mark_link_used(f"txid:{tx_id}", user.id)
    if not tx_id:
        # OCR failed to find a valid transaction ID — fall back to image hash
        photo_hash = "screenshot:" + hashlib.sha256(photo_bytes).hexdigest()
        if is_link_used(photo_hash) or is_tx_used(photo_hash):
            await update.message.reply_text(
                "❌ This screenshot was already submitted.\n\n"
                "If you think this is a mistake, contact support:\n"
                "@mezzodeposite"
            )
            return
        mark_link_used(photo_hash, user.id)
        save_tx(photo_hash, user.id)
        tx_id = "N/A (OCR failed)"

    # ── Withdraw screenshot ────────────────────────────────────────────────
    if context.user_data.get("waiting_withdraw_code"):
        context.user_data["waiting_withdraw_code"] = False
        req_id = save_pending(user.id, "withdraw", 0)

        await forward_to_all_admins(context, update.message.chat_id, update.message.message_id)
        tamper_warning = "\n⚠️ TAMPER ALERT: Image looks suspicious!" if is_tampered else ""
        await notify_all_admins(
            context,
            f"➖ Withdraw Request!\n"
            f"From: {user.first_name}\n"
            f"Username: @{user.username}\n"
            f"Telegram ID: {user.id}\n"
            f"Phone: {phone}\n"
            f"Mezzo ID: {mezzo_id}\n"
            f"Transaction ID: {tx_id}\n\n"
            f"⚠️ Minimum: 500 ETB"
            f"{tamper_warning}",
            reply_markup=admin_buttons(req_id, "withdraw")
        )
        await update.message.reply_text(
            "✅ Code screenshot received!\n"
            "We will process your withdrawal within 5 min."
        )
        return

    # ── Deposit screenshot ─────────────────────────────────────────────────
    # Use OCR-detected amount if user didn't select one from the menu
    amount_str = context.user_data.get("deposit_amount", "0")
    if str(amount_str).isdigit() and int(amount_str) > 0:
        amount = int(amount_str)
    elif ocr_amount and ocr_amount.isdigit():
        amount = int(ocr_amount)
    else:
        amount = 0
    req_id = save_pending(user.id, "deposit", amount)

    await forward_to_all_admins(context, update.message.chat_id, update.message.message_id)
    tamper_warning = "\n⚠️ TAMPER ALERT: Image looks suspicious!" if is_tampered else ""
    await notify_all_admins(
        context,
        f"💰 New Deposit!\n"
        f"From: {user.first_name}\n"
        f"Username: @{user.username}\n"
        f"Telegram ID: {user.id}\n"
        f"Phone: {phone}\n"
        f"Mezzo ID: {mezzo_id}\n"
        f"Transaction ID: {tx_id}\n"
        f"Amount: {amount if amount else '?'} ETB"
        f"{tamper_warning}",
        reply_markup=admin_buttons(req_id, "deposit")
    )
    await update.message.reply_text("✅ Screenshot received! We confirm within 5 min.")

# ── Admin broadcast ───────────────────────────────────────────────────────────

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    context.user_data["waiting_broadcast"] = True
    await update.message.reply_text(
        "📣 BROADCAST\n\n"
        "Type the message you want to send to all users.\n"
        "You can also send a photo with a caption.\n\n"
        "Send /cancel to cancel."
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    context.user_data["waiting_broadcast"] = False
    await update.message.reply_text("❌ Broadcast cancelled.")

# ── Admin management (super admin only) ──────────────────────────────────────

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_super_admin(update.message.from_user.id):
        await update.message.reply_text("⛔ Only the super admin can add admins.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /addadmin USER_ID")
        return
    new_admin_id = int(context.args[0])
    if is_admin(new_admin_id):
        await update.message.reply_text("⚠️ This user is already an admin.")
        return
    add_admin(new_admin_id, f"Admin {new_admin_id}", update.message.from_user.id)
    await update.message.reply_text(f"✅ User {new_admin_id} added as admin.")
    try:
        await context.bot.send_message(
            chat_id=new_admin_id,
            text="✅ You have been added as an admin of Mezzo Bot!"
        )
    except Exception:
        pass

async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_super_admin(update.message.from_user.id):
        await update.message.reply_text("⛔ Only the super admin can remove admins.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin USER_ID")
        return
    target_id = int(context.args[0])
    if target_id == ADMIN_ID:
        await update.message.reply_text("⛔ Cannot remove the super admin.")
        return
    if not is_admin(target_id):
        await update.message.reply_text("⚠️ This user is not an admin.")
        return
    remove_admin(target_id)
    await update.message.reply_text(f"✅ User {target_id} removed from admins.")
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text="❌ You have been removed as an admin of Mezzo Bot."
        )
    except Exception:
        pass

async def listadmins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    admins = get_all_admins()
    lines = []
    for uid, name, added_at in admins:
        tag = " 👑" if uid == ADMIN_ID else ""
        lines.append(f"• {name} (ID: {uid}){tag}\n  Added: {added_at[:16]}")
    text = "👮 ADMINS\n\n" + "\n\n".join(lines)
    await update.message.reply_text(text)

# ── Admin confirm (kept as backup) ────────────────────────────────────────────

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("Usage: /confirm USER_ID AMOUNT")
        return
    user_id = int(context.args[0])
    amount  = int(context.args[1])
    if get_user(user_id):
        add_balance(user_id, amount)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Deposit Confirmed!\nAmount: {amount} ETB added\nThank you! 🎉"
        )
        await update.message.reply_text("✅ Done!")
    else:
        await update.message.reply_text("❌ User not found.")

# ── Manual balance adjust ─────────────────────────────────────────────────────

async def addbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /addbalance USER_ID AMOUNT\n\n"
            "Example: /addbalance 123456789 500"
        )
        return
    try:
        user_id = int(context.args[0])
        amount  = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ USER_ID and AMOUNT must be numbers.")
        return
    if amount <= 0:
        await update.message.reply_text("⚠️ Amount must be greater than 0.")
        return

    target = get_user(user_id)
    if not target:
        await update.message.reply_text("❌ User not found.")
        return

    add_balance(user_id, amount)
    new_balance = get_balance(user_id)

    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"💰 Balance Updated!\n\n"
                f"➕ {amount} ETB has been added to your account.\n"
                f"New balance: {new_balance} ETB"
            )
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Added {amount} ETB to {target['name']} (ID: {user_id})\n"
        f"New balance: {new_balance} ETB"
    )

async def removebalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /removebalance USER_ID AMOUNT\n\n"
            "Example: /removebalance 123456789 200"
        )
        return
    try:
        user_id = int(context.args[0])
        amount  = int(context.args[1])
    except ValueError:
        await update.message.reply_text("⚠️ USER_ID and AMOUNT must be numbers.")
        return
    if amount <= 0:
        await update.message.reply_text("⚠️ Amount must be greater than 0.")
        return

    target = get_user(user_id)
    if not target:
        await update.message.reply_text("❌ User not found.")
        return

    success = remove_balance(user_id, amount)
    if not success:
        current = get_balance(user_id)
        await update.message.reply_text(
            f"❌ Not enough balance.\n"
            f"{target['name']} only has {current} ETB."
        )
        return

    new_balance = get_balance(user_id)

    # Notify the user
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"💰 Balance Updated!\n\n"
                f"➖ {amount} ETB has been deducted from your account.\n"
                f"New balance: {new_balance} ETB"
            )
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ Removed {amount} ETB from {target['name']} (ID: {user_id})\n"
        f"New balance: {new_balance} ETB"
    )

# ── Send message to specific user ────────────────────────────────────────────

async def sendmsg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /sendmsg USER_ID your message here\n\n"
            "Example: /sendmsg 123456789 Your deposit is being reviewed."
        )
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("⚠️ USER_ID must be a number.")
        return

    message = " ".join(context.args[1:])
    target = get_user(user_id)
    if not target:
        await update.message.reply_text("❌ User not found.")
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📩 Message from Mezzo Bot:\n\n{message}"
        )
        await update.message.reply_text(
            f"✅ Message sent to {target['name']} (ID: {user_id})"
        )
    except Exception:
        await update.message.reply_text(
            f"❌ Could not send message to {target['name']}.\n"
            f"They may have blocked the bot."
        )

    # Also store who the admin is talking to for reply context
    context.user_data["reply_to_user"] = user_id
    context.user_data["reply_to_name"] = target["name"]

async def replymsg_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reply to the last user you messaged without typing the ID again."""
    if not is_admin(update.message.from_user.id):
        return
    user_id = context.user_data.get("reply_to_user")
    if not user_id:
        await update.message.reply_text(
            "⚠️ No recent user to reply to.\n"
            "Use /sendmsg USER_ID message first."
        )
        return
    if not context.args:
        await update.message.reply_text(
            f"Usage: /reply your message here\n\n"
            f"This will reply to: {context.user_data.get('reply_to_name')} (ID: {user_id})"
        )
        return

    message = " ".join(context.args)
    name = context.user_data.get("reply_to_name", str(user_id))

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📩 Message from Mezzo Bot:\n\n{message}"
        )
        await update.message.reply_text(f"✅ Reply sent to {name} (ID: {user_id})")
    except Exception:
        await update.message.reply_text(
            f"❌ Could not send message to {name}.\n"
            f"They may have blocked the bot."
        )

# ── View all pending requests ─────────────────────────────────────────────────

async def pending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.message.from_user.id):
        return

    rows = get_all_pending()

    if not rows:
        await update.message.reply_text("✅ No pending requests right now.")
        return

    deposits  = [r for r in rows if r[2] == "deposit"]
    withdraws = [r for r in rows if r[2] == "withdraw"]

    lines = [f"📋 PENDING REQUESTS ({len(rows)} total)\n"]

    if deposits:
        lines.append(f"💰 DEPOSITS ({len(deposits)})")
        for req_id, user_id, _, amount, created_at, name, mezzo_id, phone in deposits:
            lines.append(
                f"• #{req_id} — {name or 'Unknown'}\n"
                f"  Mezzo ID: {mezzo_id or '?'} | Phone: {phone or '?'}\n"
                f"  Amount: {amount if amount else '?'} ETB\n"
                f"  Time: {created_at[:16]}"
            )

    if withdraws:
        lines.append(f"\n➖ WITHDRAWALS ({len(withdraws)})")
        for req_id, user_id, _, amount, created_at, name, mezzo_id, phone in withdraws:
            lines.append(
                f"• #{req_id} — {name or 'Unknown'}\n"
                f"  Mezzo ID: {mezzo_id or '?'} | Phone: {phone or '?'}\n"
                f"  Time: {created_at[:16]}"
            )

    # Telegram has a 4096 char limit — split if needed
    message = "\n".join(lines)
    if len(message) > 4000:
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(message)

# ── Main ──────────────────────────────────────────────────────────────────────

init_db()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu_command))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("broadcast", broadcast_command))
app.add_handler(CommandHandler("cancel", cancel_command))
app.add_handler(CommandHandler("addadmin", addadmin_command))
app.add_handler(CommandHandler("removeadmin", removeadmin_command))
app.add_handler(CommandHandler("listadmins", listadmins_command))
app.add_handler(CommandHandler("addbalance", addbalance_command))
app.add_handler(CommandHandler("removebalance", removebalance_command))
app.add_handler(CommandHandler("sendmsg", sendmsg_command))
app.add_handler(CommandHandler("reply", replymsg_command))
app.add_handler(CommandHandler("pending", pending_command))
app.add_handler(CallbackQueryHandler(button_click))
app.add_handler(MessageHandler(filters.CONTACT, receive_contact))
app.add_handler(MessageHandler(filters.PHOTO, receive_screenshot))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))

print("Bot is running...")
app.run_polling()
