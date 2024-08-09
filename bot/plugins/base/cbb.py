from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from bot.options import options
import random

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()

    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'),
            InlineKeyboardButton('⍟ Aʙᴏᴜᴛ', callback_data='about'),
        ],[
            InlineKeyboardButton('👨🏻‍💻 Aᴅᴍɪɴ 👨🏻‍💻', url=f't.me/YoeNaung')
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(options.settings.PICS.split()))
        )
        await query.message.edit_text(
            text=options.settings.START_MESSAGE.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
        ]]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(options.settings.PICS.split()))
        )
        await query.message.edit_text(
            text=options.settings.HELP_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('Sᴏᴜʀᴄᴇ Cᴏᴅᴇ', callback_data='source')
        ],[
            InlineKeyboardButton('Hᴏᴍᴇ', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(options.settings.PICS.split()))
        )
        await query.message.edit_text(
            text=options.settings.ABOUT_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('⟸ Bᴀᴄᴋ', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(options.settings.PICS.split()))
        )
        await query.message.edit_text(
            text=options.settings.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    if query.data.startswith("delfile"):
        ident, file_unique_id = query.data.split("#")
        await query.answer(url=f"https://t.me/{client.me.username}?start={file_unique_id}")
