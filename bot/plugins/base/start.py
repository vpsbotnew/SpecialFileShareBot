from typing import Union
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import random, os, asyncio
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram import Client
from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, DataValidationError, PyroHelper, RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import FileResolverModel, HelpCmd, Pyrotools
from bot.utilities.schedule_manager import schedule_manager




database = MongoDB(database=config.MONGO_DB_NAME)

class FileSender:
    """Used to manage file sending functions between codexbotz and teleshare."""

    @staticmethod
    async def codexbotz(
        client: Client,
        codex_message_ids: list[int],
        chat_id: int,
        from_chat_id: int,
        protect_content: bool,  # noqa: FBT001
    ) -> Union[Message, list[Message]]:
        if len(codex_message_ids) == 1:
            send_files = await client.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=codex_message_ids[0],
                protect_content=protect_content,
            )
        else:
            send_files = await client.forward_messages(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_ids=codex_message_ids,
                hide_sender_name=True,
                protect_content=protect_content,
            )
        return send_files

    @staticmethod
    async def teleshare(
        client: Client,
        chat_id: int,
        file_data: list[FileResolverModel],
        file_origin: int,
        protect_content: bool,  # noqa: FBT001
    ) -> Union[Message, list[Message]]:
        if len(file_data) == 1:
            send_files = await Pyrotools.send_media(
                client=client,
                chat_id=chat_id,
                file_data=file_data[0],
                protect_content=protect_content,
            )
        else:
            send_files = await Pyrotools.send_media_group(
                client=client,
                chat_id=chat_id,
                file_data=file_data,
                file_origin=file_origin,
                protect_content=protect_content,
            )
        return send_files


@Client.on_message(
    filters.command("start") & filters.private & PyroFilters.subscription(),
    group=0,
)
@RateLimiter.hybrid_limiter(func_count=1)
async def file_start(
    client: Client,
    message: Message,
) -> Message:
    if not message.command[1:]:
        buttons = [
            [InlineKeyboardButton('〄 Hᴇʟᴘ', callback_data='help'), InlineKeyboardButton('⍟ Aʙᴏᴜᴛ', callback_data='about')],[
            InlineKeyboardButton('👨🏻‍💻 Aᴅᴍɪɴ 👨🏻‍💻', url=f't.me/YoeNaung')]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)
    
        await client.send_photo(
            chat_id=message.chat.id,
            photo=random.choice(options.settings.PICS.split()),
            caption=options.settings.START_MESSAGE.format(message.from_user.mention),
            reply_markup=reply_markup
        )
        return message.stop_propagation()

    await database.update_one(
        collection="Users",
        db_filter={"_id": message.from_user.id, "username": message.from_user.first_name},
        update={"$set": {"_id": message.from_user.id, "username": message.from_user.first_name}},
        upsert=True,
    )

    base64_file_link = message.text.split(maxsplit=1)[1]
    file_document = await database.aggregate(collection="Files", pipeline=[{"$match": {"_id": base64_file_link}}])

    if not file_document:
        try:
            codex_message_ids = DataEncoder.codex_decode(
                base64_string=base64_file_link,
                backup_channel=config.BACKUP_CHANNEL,
            )
        except DataValidationError:
            await message.reply(text="Attempted to resolve link: Got invalid link.")
            return message.stop_propagation()

        send_files = await FileSender.codexbotz(
            client=client,
            codex_message_ids=codex_message_ids,
            chat_id=message.chat.id,
            from_chat_id=config.BACKUP_CHANNEL,
            protect_content=config.PROTECT_CONTENT,
        )
    else:
        file_document = file_document[0]
        file_origin = file_document["file_origin"]
        file_data = [FileResolverModel(**file) for file in file_document["files"]]

        send_files = await FileSender.teleshare(
            client=client,
            chat_id=message.chat.id,
            file_data=file_data,
            file_origin=file_origin,
            protect_content=config.PROTECT_CONTENT,
        )

    delete_n_seconds = options.settings.AUTO_DELETE_SECONDS

    if delete_n_seconds != 0:
        schedule_delete_message = [msg.id for msg in send_files] if isinstance(send_files, list) else [send_files.id]
        auto_delete_message = (
            options.settings.AUTO_DELETE_MESSAGE.format(int(delete_n_seconds / 60))
            if not isinstance(options.settings.AUTO_DELETE_MESSAGE, int)
            else options.settings.AUTO_DELETE_MESSAGE
        )
        auto_delete_message_reply = await PyroHelper.option_message(
            client=client,
            message=message,
            option_key=auto_delete_message,
        )
        schedule_delete_message.append(auto_delete_message_reply.id)

        await schedule_manager.schedule_delete(
            client=client,
            chat_id=message.chat.id,
            message_ids=schedule_delete_message,
            delete_n_seconds=delete_n_seconds,
        )
    return message.stop_propagation()


@Client.on_message(filters.command("start") & filters.private, group=1)
@RateLimiter.hybrid_limiter(func_count=1)
async def return_start(
    client: Client,
    message: Message,
) -> None:
    channels_n_invite = client.channels_n_invite  # type: ignore[reportAttributeAccessIssue]
    buttons = []

    for channel, invite in channels_n_invite.items():
        buttons.append([InlineKeyboardButton(text=channel, url=invite)])

    if message.command[1:]:
        link = f"https://t.me/{client.me.username}?start={message.command[1]}"  # type: ignore[reportOptionalMemberAccess]
        buttons.append([InlineKeyboardButton(text="♻️  Try Again ♻️", url=link)])

    reply_markup = InlineKeyboardMarkup(buttons)
    
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(options.settings.PICS.split()),
        caption=options.settings.FORCE_SUB_MESSAGE.format(message.from_user.mention),
        reply_markup=reply_markup
    )


HelpCmd.set_help(
    command="start",
    description=file_start.__doc__,
    allow_global=True,
    allow_non_admin=True,
)
