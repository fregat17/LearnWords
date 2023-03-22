from os import environ

from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BufferedInputFile


from airtable_base.fetch import AirtableActions
from airtable_base.middleware import AirtableMiddleware

# tokens
BOT_TOKEN = environ['BOT_TOKEN']
AIRTABLE_TOKEN = environ["AIRTABLE_TOKEN"]
BASE = environ["WORDS_BASE"]


async def go_anneal(m: Message, air_connect: AirtableActions):
    additional_data = air_connect.get_df(["Иероглиф", "Пиньинь"])
    additional_data.to_dict(orient='records')
    print(additional_data)


def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, BASE, "Слова")))
    dp.message.register(go_anneal)

    dp.run_polling(bot)


if __name__ == "__main__":
    main()


