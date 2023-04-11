import asyncio
import operator
from os import environ
from random import choice

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
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
WORDS_BASE = environ["WORDS_BASE"]


class DialogSG(StatesGroup):
    entry = State()
    learning = State()


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.entry, mode=StartMode.RESET_STACK)


async def get_flags(**kwargs):
    flags = [
        ("Иероглиф", "hieroglyph"),
        ("Пиньинь", "pinyin"),
        ("Значение", "meaning"),
    ]

    return {
        "flags": flags,
    }


async def get_data(dialog_manager: DialogManager, air_connect, **kwargs):
    flags = dialog_manager.dialog_data.get("chosen_flags")
    data = air_connect.get_fields(["Hieroglyph", "Pinyin", "Meaning", "Haohan", "TrainCh"])
    cards = make_cards(data)
    card = choice(cards)

    if "hieroglyph" in flags:
        dialog_manager.dialog_data["right_hieroglyph"] = card.hieroglyph

    return {
        "flags": flags,
        "card": card
    }


async def go_cards(c: CallbackQuery, dialog, manager: DialogManager):
    checked_flags = manager.find("regimes_kbd")
    manager.dialog_data["chosen_flags"] = checked_flags.get_checked()

    await manager.next()


async def check_hieroglyph(m: Message, dialog, manager: DialogManager):
    hieroglyph_input = m.text
    right_hieroglyph = manager.dialog_data.get("right_hieroglyph")
    if hieroglyph_input == right_hieroglyph:
        await m.answer("Верно")
    else:
        await m.answer(f"Неверно. Правильно будет так - {right_hieroglyph}")


regimes_kbd = Multiselect(
    Format("✓ {item[0]}"),  # E.g `✓ Apple`
    Format("{item[0]}"),
    id="regimes_kbd",
    item_id_getter=operator.itemgetter(1),
    items="flags",
    min_selected=1,
    max_selected=2
)

get_regime = Button(Const("Process"), id="get_regime", on_click=go_cards)
next_card = Button(Const("Next"), id="next")

card_template = Jinja("""
{% macro render_field(field) %}
    {% if field in flags %}<tg-spoiler>{{card[field]}}</tg-spoiler>{% else %}<b>{{card[field]}}</b>{% endif %}
{% endmacro %}

{% for field in ['hieroglyph', 'pinyin', 'meaning'] %}
{{ render_field(field) }}
{% endfor %}

<a href="{{card.haohan}}">haohan</a>|<a href="{{card.trainch}}">trainch</a>
""")

dialog = Dialog(
    Window(
        Const("Выбери, что конкретно будешь повторять"),
        regimes_kbd,
        get_regime,
        state=DialogSG.entry,
        getter=get_flags
    ),
    Window(
        card_template,
        next_card,
        MessageInput(check_hieroglyph, content_types=[ContentType.TEXT]),
        parse_mode=ParseMode.HTML,
        state=DialogSG.learning,
        getter=get_data,
        disable_web_page_preview=True,
    ),
)


async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.callback_query.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, WORDS_BASE, "Слова")))
    dp.message.middleware(AirtableMiddleware(AirtableActions(AIRTABLE_TOKEN, WORDS_BASE, "Слова")))

    dp.message.register(start, F.text == "/start")

    registry = DialogRegistry()
    registry.register(dialog)
    registry.setup_dp(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
