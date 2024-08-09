import dns.resolver
from pydantic import BaseModel
from pymongo.errors import ConfigurationError
from typing import Union

from bot.config import config
from bot.database import MongoDB


class SettingsModel(BaseModel):
    FORCE_SUB_MESSAGE: Union[str, int] = """Hello {}

ရုပ်ရှင်ရရှိဖိုအတွက် ဒီချန်နယ်လေးကို Join ထားရမှာပါနော်😊

Please Join Channel 😇"""

    START_MESSAGE: Union[str, int] = """Hello {}

ɪ ᴀᴍ ᴀᴅᴠᴀɴᴄᴇ ᴀɴᴅ ᴘᴏᴡᴇʀғᴜʟʟ ʙᴏᴛ ᴡɪᴛʜ ᴀᴍᴀᴢɪɴɢ ғᴇᴀᴛᴜʀᴇs ᴊᴜsᴛ ᴛʏᴘᴇ ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇɴ sᴇᴇ ᴍʏ ᴘᴏᴡᴇʀ 💘
"""

    USER_REPLY_TEXT: Union[str, int] = "idk"
    HELP_TXT: Union[str, int] = """- ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴀɴ ᴘʀɪᴠᴀᴛᴇ ꜱᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ.

- ꜱᴏᴜʀᴄᴇ - t.me/KOPAINGLAY15"""

    ABOUT_TXT: Union[str, int] = """<b>✯ Cʀᴇᴀᴛᴏʀ: <a href='https://t.me/KOPAINGLAY15'>Ko Paing</a>
✯ Lɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>Pʏʀᴏɢʀᴀᴍ</a>
✯ Lᴀɴɢᴜᴀɢᴇ: <a href='https://www.python.org/download/releases/3.0/'>Pʏᴛʜᴏɴ 3</a>
✯ DᴀᴛᴀBᴀsᴇ: <a href='https://www.mongodb.com/'>MᴏɴɢᴏDB</a>
✯ Bᴜɪʟᴅ Sᴛᴀᴛᴜs: v2.7.1 [ Sᴛᴀʙʟᴇ ]</b>"""

    SOURCE_TXT: Union[str, int] = """<b>ɴᴏᴛᴇ:
- ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴀɴ ᴘʀɪᴠᴀᴛᴇ ꜱᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ.

- ꜱᴏᴜʀᴄᴇ - t.me/KOPAINGLAY15

Dᴇᴠᴇʟᴏᴘᴇʀ:
- <a href="https://t.me/KOPAINGLAY15">Ko Paing</a></b>"""

    JOIN_MESSAGE: Union[str, int] = """<b></b>"""
    
    PICS: Union[str, int] = f"https://telegra.ph//file/7d11957f5a9ce1871d410.jpg https://telegra.ph//file/1c47d3d0d91e49f696f8d.jpg https://telegra.ph//file/eb003eb5600874d645edd.jpg https://telegra.ph//file/e31794486553839d1e28a.jpg https://telegra.ph//file/73bc7674e315da858fe74.jpg"

    AUTO_DELETE_MESSAGE: Union[str, int] = f"""<b><u>❗️❗️❗️အရေးကြီးပါတယ်❗️❗️❗️</b></u>

 ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကို  <b><u> 5 မိနစ်အတွင်း </u> </b>🫥 <i></b>(မူပိုင်ခွင့်ပြဿနာများကြောင့်) ဖျက်ပါမည်။</i></b>.


<i><b> ကျေးဇူးပြု၍ ဤဖိုင်များ/ဗီဒီယိုများအားလုံးကို သင်၏ save မက်ဆေ့ချ်များသို့ ပေးပို့ပြီး ထိုနေရာတွင် ဇာတ်ကားအားကြည့်ရူပါ။</i></b>

********

<b><u>❗️❗️❗️IMPORTANT❗️️❗️❗️</u></b>

This Movie Files/Videos will be deleted in <b><u>5 mins</u></b> 🫥 <i></b>(Due to Copyright Issues)</i></b>.

<b><i>Please forward this ALL Files/Videos to your Saved Messages and Start Download there</i></b>"""

    CAPTION: Union[str, int] = f"""

Channel လေးတွေ Add ထားပေးအုံးနော် 
https://t.me/addlist/FCNUqz3nfyM2MzBk
"""


    AUTO_DELETE_SECONDS: int = 300
    GLOBAL_MODE: bool = False
    BACKUP_FILES: bool = True


class InvalidValueError(Exception):
    def __init__(self, key: Union[str, int]) -> None:
        super().__init__(f"Value for key '{key}' must have the same type as the existing value.")


class Options:
    def __init__(self) -> None:
        """
        Initialize the Settings class.

        Parameters:
            self.settings:
                Initialized as SettingsModel.
            self.collection:
                The name of the collection.
            self.database:
                The MongoDB instance.
            self.document_id:
                The ID of the document to retrieve/update settings.
        """
        self.settings = SettingsModel()
        self.collection = "BotSettings"
        self.document_id = "MainOptions"
        try:
            self.database = MongoDB(database=config.MONGO_DB_NAME)
        except ConfigurationError:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = ["8.8.8.8"]
            self.database = MongoDB(database=config.MONGO_DB_NAME)

    async def load_settings(self) -> None:
        """
        Load settings from the MongoDB collection.

        Example:
            await self.load_settings()
        """
        pipeline = [{"$match": {"_id": self.document_id}}]
        settings_doc = await self.database.aggregate(collection=self.collection, pipeline=pipeline)

        if settings_doc:
            self.settings = SettingsModel(**settings_doc[0])
        else:
            self.settings = SettingsModel()

        update = {"$set": self.settings.model_dump()}
        db_filter = {"_id": self.document_id}

        await self.database.update_one(
            collection=self.collection,
            db_filter=db_filter,
            update=update,
        )

    async def update_settings(
        self,
        key: str,
        value: Union[str, int],
    ) -> SettingsModel:
        """
        Update the settings and save them to the MongoDB collection.

        Parameters:
            key:
                The key/field name in the SettingsModel to update.
            value:
                The new value to set for the specified key.

        Returns:
            The updated SettingsModel instance from 'self.settings'.

        Raises:
            ValueError:
                If the provided key is not a valid field in the SettingsModel.
            ValidationError:
                Failed to validate changes.

        Example:
            await self.update_settings(key="START_MESSAGE", value="Hello, I am a bot.")
        """
        if key not in self.settings.__fields__:
            raise KeyError(key)

        annotation = self.settings.__fields__[key].annotation
        if annotation is not None and not isinstance(value, annotation):
            raise InvalidValueError(key)

        setattr(self.settings, key, value)
        self.settings = SettingsModel(**self.settings.model_dump())

        model_key, model_value = key, getattr(self.settings, key)

        db_filter = {"_id": self.document_id}
        update = {"$set": {model_key: model_value}}

        await self.database.update_one(
            collection=self.collection,
            db_filter=db_filter,
            update=update,
        )

        return self.settings


# create an instance
options = Options()
