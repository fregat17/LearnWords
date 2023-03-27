from cachetools import TTLCache, cached

cache = TTLCache(maxsize=1, ttl=360)


class WordCard:
    def __init__(self, hieroglyph, pinyin, meaning, haohan, trainch):
        self.hieroglyph = hieroglyph
        self.pinyin = pinyin
        self.meaning = meaning
        self.haohan = haohan
        self.trainch = trainch


def make_cards(word_records):
    cards = []

    for record in word_records:
        if bool(record):
            cards.append(WordCard(record["Hieroglyph"],
                                  record["Pinyin"],
                                  record["Meaning"],
                                  record.get("Haohan", False),
                                  record.get("TrainCh", False)))
        else:
            continue

    return cards
