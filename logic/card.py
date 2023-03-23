class WordCard:
    def __init__(self, hieroglyph, pinyin, meaning, haohan, train):
        self.hieroglyph = hieroglyph
        self.pinyin = pinyin
        self.meaning = meaning
        self.haohan = haohan
        self.train = train


def make_cards(word_records):
    cards = []

    for record in word_records:
        if bool(record):
            cards.append(WordCard(record["Иероглиф"],
                                  record["Пиньинь"],
                                  record["Значение"],
                                  record["Хаохан"],
                                  record["ТрейнЧайниз"]))
        else:
            continue

    return cards
