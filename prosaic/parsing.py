import re
import prosaic.nlp as nlp
from prosaic.models import Phrase, Source, db_engine, Engine
from sqlalchemy.orm import sessionmaker

pairs = [('{', '}'), ('(', ')'), ('[', ']')]
bad_substrings = ['`', '“', '”', '«', '»', "''", '\\n', '\\',]
collapse_whitespace_re = re.compile("\s+")

def pre_process_text(raw_text: str) -> str:
    """Performs text-wide regex'ing we need before converting to sentences."""
    raw_text = re.sub(collapse_whitespace_re, ' ', raw_text)
    return raw_text

def pre_process_sentence(sentence: str) -> str:
    """Strip dangling pair characters. For now, strips some substrings that we
    don't want. r and lstrip. Returns modified sentence"""
    if sentence.count('"') == 1:
        sentence = sentence.replace('"', '')

    # TODO bootleg
    for l,r in pairs:
        if sentence.count(l) == 1 and sentence.count(r) == 0:
            sentence = sentence.replace(l, '')
        if sentence.count(r) == 1 and sentence.count(l) == 0:
            sentence = sentence.replace(r, '')

    # TODO collapse this into a regex and do it in pre_process_text
    for substring in bad_substrings:
       sentence = sentence.replace(substring, '')

    return sentence.rstrip().lstrip()

# TODO support source descriptions
def process_text(raw_text: str, source_name: str, db: Engine) -> None:
    """Given raw text and a source filename, adds a new source with the raw
    text as its content and then processes all of the phrases in the text."""

    print('connecting to db...')
    session = sessionmaker(db)()

    print('pre-processing text...')
    raw_text = pre_process_text(raw_text)
    source = Source(name=source_name, content=raw_text, description="todo")
    session.add(source)

    print('extracting sentences')
    sentences = nlp.sentences(raw_text)

    print("expanding clauses...")
    sentences = nlp.expand_multiclauses(sentences)

    print("pre-processing, parsing and saving sentences...")
    for x in range(0, len(sentences)):
        sentence = pre_process_sentence(sentences[x])

        phonemes = list(map(nlp.word_to_phonemes, nlp.words(sentence)))
        stems = nlp.stem_sentence(sentence)
        rhyme_sound = nlp.rhyme_sound(sentence)
        syllables = nlp.count_syllables(sentence)
        alliteration = nlp.has_alliteration(sentence)

        phrase = Phrase(stems=stems, raw=sentence, alliteration=alliteration, 
                        rhyme_sound=rhyme_sound,
                        syllables=syllables, line_no=x, source=source)
        # TODO save the thread on a coroutine or something

        session.add(phrase)

    session.commit()

    print("done")
