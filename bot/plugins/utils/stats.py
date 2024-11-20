from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters

database = MongoDB(database=config.MONGO_DB_NAME)


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("stats"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def help_command(client: Client, message: Message) -> Message:  # noqa: ARG001
    """A command to display links and users count.:

    **Usage:**
        /stats
    """

    link_count = await database.db["Files"].count_documents({})
    users_count = await database.db["Users"].count_documents({})

    return await message.reply(f">STATS:\n**Users Count:** `{users_count}`\n**Links Count:** `{link_count}`")



client = AsyncIOMotorClient(config.MONGO_DB_URL)
mydb = client[config.MONGO_DB_NAME]
dbcol = mydb["Users"]

@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("removeid"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def remove_userid(bot: Client, message: Message) -> Message:  # noqa: ARG001
    user_id = message.from_user.id
    msg = await message.reply("Please enter the user's ID to remove their premium subscription. \nType /cancel to cancel.")

    try:
        user_input = await bot.listen(user_id)
        if user_input.text == '/cancel':
            await user_input.delete()
            await msg.edit("Canceled this process.")
            return

        user_to_remove = user_input.text.strip()
        

        user_info = dbcol.find_one({"_id": int(user_to_remove)})
        
        if user_info:
            dbcol.delete_one({"_id": int(user_to_remove)})  # Delete the specific user by ID
            await message.reply(f"Removed successfully for user {user_to_remove}.")
        else:
            await message.reply(f"No User{user_to_remove}.")

        await msg.delete()

    except Exception as e:
        await msg.edit(f"Error removing premium subscription: {str(e)}")
