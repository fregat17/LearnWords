from os import environ

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from airtable_base.fetch import AirtableActions
from airtable_base.middleware import AirtableMiddleware
from logic.card import make_cards
from message_template import ReadyMsg

# tokens
BOT_TOKEN = environ['BOT_TOKEN']
AIRTABLE_TOKEN = environ["AIRTABLE_TOKEN"]
BASE = environ["WORDS_BASE"]


async def go_anneal(m: Message, air_connect: AirtableActions):
    word_records = air_connect.get_fields(["Иероглиф", "Пиньинь", "Значение", "Хаохан", "ТрейнЧайниз"])
    print(word_records[0:2])
    cards = make_cards(word_records[0:2])
    print(cards)
    test = ReadyMsg(cards[1], target="hieroglyph").render()

    await m.answer(test, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)


def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, BASE, "Слова")))
    dp.message.register(go_anneal)

    dp.run_polling(bot)


if __name__ == "__main__":
    main()


