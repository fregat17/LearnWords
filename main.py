from os import environ

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select
from aiogram_dialog.widgets.text import Const, Format

from airtable_base.fetch import AirtableActions
from airtable_base.middleware import AirtableMiddleware
from logic.card import make_cards
from message_template import ReadyMsg

# tokens
BOT_TOKEN = environ['BOT_TOKEN']
AIRTABLE_TOKEN = environ["AIRTABLE_TOKEN"]
BASE = environ["WORDS_BASE"]


class DialogSG(StatesGroup):
    entry = State()
    learning = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    age = dialog_manager.current_context().dialog_data.get("age", None)
    return {
        "name": dialog_manager.current_context().dialog_data.get("name", ""),
        "age": age,
        "can_smoke": age in ("18-25", "25-40", "40+"),
    }


async def go_anneal(m, dialog, manager, air_connect: AirtableActions):
    word_records = air_connect.get_fields(["Иероглиф", "Пиньинь", "Значение", "Хаохан", "ТрейнЧайниз"])
    print(word_records[0:2])
    cards = make_cards(word_records[0:2])
    print(cards)
    test = ReadyMsg(cards[1], target="hieroglyph").render()

    manager.current_context().dialog_data["age"] = cards

    await m.answer(test, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)


dialog = Dialog(
    Window(
        Const("Greetings! Please, introduce yourself:"),
        Select(
            Format("{item}"),
            items=["0-12", "12-18", "18-25", "25-40", "40+"],
            item_id_getter=lambda x: x,
            id="w_age",
            on_click=on_age_changed,
        ),
        state=DialogSG.entry,
    ),
    Window(
        Format("{name}! How old are you?"),
        MessageInput(name_handler),
        state=DialogSG.learning,
        getter=get_data,
        preview_data={"name": "Tishka17"}
    ),
    Window(
        Multi(
            Format("{name}! Thank you for your answers."),
            Const("Hope you are not smoking", when="can_smoke"),
            sep="\n\n",
        ),
        Row(
            Back(),
            SwitchTo(Const("Restart"), id="restart", state=DialogSG.greeting),
            Button(Const("Finish"), on_click=on_finish, id="finish"),
        ),
        getter=get_data,
        state=DialogSG.finish,
    )
)


def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, BASE, "Слова")))
    dp.message.register(go_anneal)

    dp.run_polling(bot)


if __name__ == "__main__":
    main()


