import asyncio
import operator
from os import environ

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, DialogRegistry, StartMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Select, Radio, Multiselect, Button
from aiogram_dialog.widgets.text import Const, Format, Jinja

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


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.entry, mode=StartMode.RESET_STACK)


async def get_flags(**kwargs):
    flags = [
        ("hieroglyph", "hieroglyph"),
        ("pinyin", "pinyin"),
        ("meaning", "meaning"),
    ]

    return {
        "flags": flags,
    }


async def get_data(dialog_manager: DialogManager, air_connect, **kwargs):
    flags = dialog_manager.dialog_data.get("chosen_flags")
    data = air_connect.get_fields(["Hieroglyph", "Pinyin", "Meaning", "Haohan", "TrainCh"])
    cards = make_cards(data)
    ready_template = render_spoilers(flags)

    return {
        "ready_template": ready_template,
        "card": cards[23]
    }

async def go_anneal(c, dialog, manager: DialogManager):  # , air_connect: AirtableActions
    checked_flags = manager.find("regimes_kbd")
    manager.dialog_data["chosen_flags"] = checked_flags.get_checked()

    await c.answer("asd")
    await manager.next()
    #word_records = air_connect.get_fields(["Hieroglyph", "Pinyin", "Meaning", "Haohan", "TrainCh"])
    #print(word_records[0:2])


    # cards = make_cards(word_records[0:2])
    # print(cards)
    # test = ReadyMsg(cards[1], target="hieroglyph").render()
    #
    # manager.current_context().dialog_data["age"] = cards
    #
    # await m.answer(test, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)


regimes_kbd = Multiselect(
    Format("✓ {item[0]}"),  # E.g `✓ Apple`
    Format("{item[0]}"),
    id="regimes_kbd",
    item_id_getter=operator.itemgetter(1),
    items="flags",
    min_selected=1,
    max_selected=2
)

get_regime = Button(Const("Process"), id="get_regime", on_click=go_anneal)


def render_spoilers(flags):
    template = """
<b>{{card.hieroglyph}}</b>
<b>{{card.pinyin}}</b>
<b>{{card.meaning}}</b>

<a href="{{card.haohan}}">haohan</a>|<a href="{{card.trainch}}">trainch</a>
"""

    if "hieroglyph" in flags:
        template = template.replace("<b>{{card.hieroglyph}}</b>", "<span class=\"tg-spoiler\">{{card.hieroglyph}}</span>")
    if "pinyin" in flags:
        template = template.replace("<b>{{card.pinyin}}</b>", "<span class=\"tg-spoiler\">{{card.pinyin}}</span>")
    if "meaning" in flags:
        template = template.replace("<b>{{card.meaning}}</b>", "<span class=\"tg-spoiler\">{{card.meaning}}</span>")

    return template



#spoiler

dialog = Dialog(
    Window(
        Const("Выбери, что конкретно будешь повторять"),
        regimes_kbd,
        get_regime,
        state=DialogSG.entry,
        getter=get_flags
    ),
    Window(
        Jinja(),
        parse_mode=ParseMode.HTML,
        state=DialogSG.learning,
        getter=get_data,
        disable_web_page_preview=True
    ),
)


# def main():
#     bot = Bot(token=BOT_TOKEN)
#     dp = Dispatcher(storage=MemoryStorage())
#
#     dp.message.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, BASE, "Слова")))
#     dp.message.register(go_anneal)
#
#     dp.run_polling(bot)
# if __name__ == "__main__":
#     main()

def new_registry():
    registry = DialogRegistry()
    registry.register(dialog)
    return registry


async def main():
    # real main
    bot = Bot(token=BOT_TOKEN)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.callback_query.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, BASE, "Слова")))
    dp.message.register(start, F.text == "/start")

    registry = new_registry()
    registry.setup_dp(dp)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
