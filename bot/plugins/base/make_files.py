from typing import Optional

import asyncio
from typing import Any, ClassVar, TypedDict

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import HelpCmd
from imdb import Cinemagoer
imdb = Cinemagoer() 

class CacheEntry(TypedDict):
    """Cache entry for files."""

    counter: int
    files: list[dict]
    file_name: Optional[str]

class MakeFilesCommand:
    """Make files command class."""

    database: MongoDB = MongoDB(database=config.MONGO_DB_NAME)
    files_cache: ClassVar[dict[int, CacheEntry]] = {}

    @staticmethod
    @RateLimiter.hybrid_limiter(func_count=1)
    async def message_reply(client: Client, message: Message, **kwargs: Any) -> Message:
        """
        Replies to a message with rate limiter.

        Parameters:
            client (Client): The client instance.
            message (Message): The message to reply to.
            **kwargs (Any): Additional keyword arguments for the reply.

        Returns:
            Message: The replied message.
        """
        return await message.reply(**kwargs)

    @classmethod
    async def handle_convo_start(cls, client: Client, message: ConvoMessage) -> Optional[Message]:
        """
        Handle conversation start.

        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message: The replied message.
        """
        unique_id = message.chat.id + message.from_user.id
        cls.files_cache.setdefault(unique_id, {"files": [], "counter": 0, "file_name": None})
        return await cls.message_reply(client=client, message=message, text="Please send the file name.", quote=True)


    @classmethod
    async def handle_file_name(cls, client: Client, message: ConvoMessage) -> Optional[Message]:
        """
        Handle the file name input.

        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message: The replied message.
        """
        unique_id = message.chat.id + message.from_user.id
        file_name = message.text
        cls.files_cache[unique_id]["file_name"] = file_name

        return await cls.message_reply(client=client, message=message, text="Send your files.", quote=True)


    @classmethod
    async def handle_conversation(cls, client: Client, message: ConvoMessage) -> Optional[Message]:
        """
        Handle conversations and file uploads. Maintain file cache for optimization.
        Process burst files, responding only when complete.

        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message or None: The replied message or None if burst is triggered.
        """
        unique_id = message.chat.id + message.from_user.id

        # Check if file name is provided, if not, prompt for it
        if not cls.files_cache[unique_id].get("file_name"):
            return await cls.handle_file_name(client=client, message=message)

        file_type = message.document or message.video or message.photo or message.audio

        if not file_type:
            return await cls.message_reply(client=client, message=message, text="Only send files!", quote=True)

        cls.files_cache[unique_id]["counter"] += 1
        cls.files_cache[unique_id]["files"].append(
            {
                "caption": message.caption.markdown if message.caption else None,
                "file_id": file_type.file_id,
                "file_name": getattr(file_type, "file_name", file_type.file_unique_id) or file_type.file_unique_id,
                "message_id": message.id,
            },
        )

        current_files_count = cls.files_cache[unique_id]["counter"]
        await asyncio.sleep(0.1)
        if cls.files_cache[unique_id]["counter"] != current_files_count:
            return None

        file_names = "\n".join(i["file_name"] for i in cls.files_cache[unique_id]["files"])
        extra_message = "- Send more documents for batch files.\n- Send /send_link to create a sharable link."
        return await cls.message_reply(
            client=client,
            message=message,
            text=f"```\nFiles:\n{file_names}\n```\n{extra_message}",
            quote=True,
        )

    @classmethod
    async def handle_convo_stop(cls, client: Client, message: ConvoMessage) -> Optional[Message]:
        """
        Handle the end of conversation.

        This finalizes the conversation by:
        - Checking if any files were uploaded.
        - Optionally forwarding files to a backup channel.
        - Storing file information in a database.
        - Generating and sending a link to access the files.

        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message: The replied message.
        """
        unique_id = message.chat.id + message.from_user.id
        user_cache = [i["message_id"] for i in cls.files_cache[unique_id]["files"]]

        if not user_cache:
            cls.files_cache.pop(unique_id)
            return await cls.message_reply(
                client=client,
                message=message,
                text="No file inputs, stopping task.",
                quote=True,
            )

        files_to_store = []
        if options.settings.BACKUP_FILES:
            forwarded_messages = await client.forward_messages(
                chat_id=config.BACKUP_CHANNEL,
                from_chat_id=message.chat.id,
                message_ids=user_cache,
                hide_sender_name=True,
            )

            for msg in forwarded_messages if isinstance(forwarded_messages, list) else [forwarded_messages]:
                file_type = msg.document or msg.video or msg.photo or msg.audio
                files_to_store.append(
                    {
                        "caption": msg.caption.markdown if msg.caption else None,
                        "file_id": file_type.file_id,
                        "message_id": msg.id,
                    },
                )
        else:
            files_to_store = [
                {k: v for k, v in i.items() if k != "file_name"} for i in cls.files_cache[unique_id]["files"]
            ]

        file_link = DataEncoder.encode_data(str(message.date))
        file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id
        total_file_name = cls.files_cache[unique_id]["file_name"]
        chat_id = message.chat.id
        await cls.database.update_one(
            collection="Files",
            db_filter={"_id": file_link},
            update={"$set": {"file_origin": file_origin, "files": files_to_store, "total_file_name": total_file_name, "chat_id": chat_id}},
        )

        cls.files_cache.pop(unique_id)

        link = f"https://t.me/{client.me.username}?start={file_link}"  # type: ignore[reportOptionalMemberAccess]
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Copy URL", url=link)],
            [InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={link}")]],
        )

        return await cls.message_reply(
            client=client,
            message=message,
            text=f"Here is your link:\n>{link}",
            quote=True,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.create_conversation_filter(
        convo_start="/send_files",
        convo_stop="/send_link",
    ),
)
async def make_files_command_handler(client: Client, message: ConvoMessage) -> Optional[Message]:
    """Handles a conversation that receives files to generate an accessible file link.

    **Usage:**
        /send_files: initiate a conversation then send your file name and files.
        /send_link: wraps the conversation and generates a link.
    """
    if message.convo_start:
        return await MakeFilesCommand.handle_convo_start(client=client, message=message)
    if message.conversation:
        return await MakeFilesCommand.handle_conversation(client=client, message=message)
    if message.convo_stop:
        return await MakeFilesCommand.handle_convo_stop(client=client, message=message)
    return None

HelpCmd.set_help(
    command="send_files",
    description=make_files_command_handler.__doc__,
    allow_global=True,
    allow_non_admin=False,
)
