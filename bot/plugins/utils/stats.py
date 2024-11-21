from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import HelpCmd

# Initialize the database connection
database = MongoDB(database=config.MONGO_DB_NAME)
dbcol = database.db["Users"]

@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("stats"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def stats_command(client: Client, message: Message) -> None:
    """
    A command to display links and users count.

    Usage:
        /stats
    """
    try:
        link_count = await database.db["Files"].count_documents({})
        users_count = await database.db["Users"].count_documents({})

        await message.reply(
            f"**STATS:**\n"
            f"**Users Count:** `{users_count}`\n"
            f"**Links Count:** `{link_count}`"
        )
    except Exception as e:
        await message.reply(f"Error fetching stats: {str(e)}")


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("removeid"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def remove_userid(client: Client, message: Message) -> None:
    """
    Command to remove a user from the database by their user ID.

    Usage:
        /removeid <user_id>
    """
    if len(message.text.split()) == 1:
        await message.reply_text(
            "Please enter the user's ID to remove.\n\nType `/cancel` to cancel."
        )
        return

    try:
        # Extract user ID from the command
        user_to_remove = message.text.split(' ')[1]

        # Validate the user ID
        if not user_to_remove.isdigit():
            await message.reply_text("Invalid ID format. Please enter a numeric ID.")
            return

        user_to_remove = int(user_to_remove)

        # Check if the user exists in the database
        user_info = await dbcol.find_one({"_id": user_to_remove})
        if user_info:
            await dbcol.delete_one({"_id": user_to_remove})  # Remove the user
            await message.reply_text(f"Successfully removed user with ID `{user_to_remove}`.")
        else:
            await message.reply_text(f"No user found with ID `{user_to_remove}`.")
    except Exception as e:
        await message.reply_text(f"Error during the removal process: {str(e)}")


# Register the help command
HelpCmd.set_help(
    command="removeid",
    description=remove_userid.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
