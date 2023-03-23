from logic.card import WordCard


class ReadyMsg:
    def __init__(self, card: WordCard, target: str):
        self._card = card
        self._target = target

    def render(self):
        hieroglyph = self._card.hieroglyph if self._target != "hieroglyph" else f'||{self._card.hieroglyph}||'
        pinyin = self._card.pinyin if self._target != "pinyin" else f'||{self._card.pinyin}||'
        meaning = self._card.meaning if self._target != "" else f'||{self._card.meaning}||'
        haohan = self._card.haohan if bool(self._card.haohan) else "haohan"
        trainch = self._card.train if bool(self._card.haohan) else "trainch"

        text = f"{hieroglyph}\n" \
               f"{pinyin}\n\n" \
               f"{meaning}\n\n" \
               f"[haohan]({haohan})\|[trainch]({trainch})"

        return text
