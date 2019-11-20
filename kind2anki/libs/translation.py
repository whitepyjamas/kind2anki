from json import loads


class Translation:
    ts: str   # transcription
    tr: list  # translations
    ex: str   # example

    def __init__(self, tr: list, ts: str, ex: str):
        self.tr = tr
        self.ts = ts
        self.ex = ex

    def __str__(self):
        return f'ts: {self.ts} tr: {self.tr} ex: {self.ex}'


def parse(answer: str) -> Translation:
    if not answer:
        raise ValueError('answer empty')

    parsed = loads(answer)
    if not parsed:
        raise ValueError('answer empty parse')

    target = parsed['def'][:3]
    if not target:
        raise ValueError('answer empty result')

    examples = target[0]['tr'][0].get('ex')
    translations = [t['tr'][0]['text'] for t in target]

    return Translation(
        tr=translations,
        ts=target[0].get('ts'),
        ex=examples[0]['text'] if examples else None)
