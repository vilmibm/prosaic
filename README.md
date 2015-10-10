                                   o
           _   ,_    __   ,   __,      __
         |/ \_/  |  /  \_/ \_/  |  |  /
         |__/    |_/\__/  \/ \_/|_/|_/\___/
        /|
        \|

# prosaic

being a prose scraper & cut-up poetry generator

by [nathanielksmith](http://chiptheglasses.com)

using [nltk](http://nltk.org)

and licensed under the [GPL](https://www.gnu.org/copyleft/gpl.html).

## what is prosaic?

prosaic is a tool for
[cutting up](https://en.wikipedia.org/wiki/Cut-up_technique) large quantities of
text that a poet can then derive poetry from by writing templates that describe
a poem line by line.

## prerequisites

* mongodb 2.0+ (see explanation at bottom)
* python 3.4+
* linux (it has also been verified to work fine on osx)
* you might need some -dev libraries to get nltk to compile

## quick start

    $ pip install prosaic
    $ prosaic corpus loadfile pride_and_prejudice.txt
    $ prosaic poem new

      -- and so I warn you.
      We_will_ know where we have gone
      Mr. Darcy smiled

## slow start

    # install mongodb / python3 / virtualenv for your platform
    $ virtualenv poetry
    $ source poetry/bin/activate
    $ pip install prosaic
    # wait a bit, nltk compiles some stuff
    # find some text, maybe from project gutenberg
    $ prosaic corpus loadfile pride_and_prejudice.txt
    $ prosaic corpus loadfile call_of_cthulhu.txt
    $ prosaic poem new -t sonnet

      Her colour changed, and she said no more.
      They saw much to interest, but nothing to justify inquiry.
      sir, I do indeed.
      Elizabeth could not but look surprised.
     `` I am talking of possibilities, Charles.''
     `` Can it be possible that he will marry her?''
     `` I am talking of possibilities, Charles.''
      He looked surprised, displeased, alarmed
     `` You can not be too much upon your guard.
      One Survivor and Dead Man Found Aboard.
      It had not been very great
     :-- but let me not interrupt you, sir.
      Mrs. Bennet said only,`` Nonsense, nonsense!''
      She could not bear such suspense

## use as a library

```python
from pymongo import MongoClient
from prosaic.nyarlathotep import process_text
from prosaic.cthulhu import poem_from_template

db = MongoClient().my_corpus_db.phrases
process_text("some very long string of text", "a name for this long string of text", db)

# poem_from_template returns raw line dictionaries from the database:
poem_lines = poem_from_template([{'syllables': 5}, {'syllables':7}, {'syllables':5}], db)

# pull raw text out of each line dictionary and print it:
print(list(map(lambda l: l['raw'], poem_lines)))
```

## write a template

Templates are currently stored as json files (or passed from within code as
python dictionaries) that represent an array of json objects, each one
containing describing a line of poetry.

A template describes a "desired" poem. Prosaic uses the template to approximate a piece given what text it has in its database. Running prosaic repeatedly with the same template will almost always yield different results.

You can see available templates with `prosaic template ls`, edit them with `prosaic template edit <template name>`, and add your own with `prosaic template new <template name>`.

The rules available are:

* _syllables_: integer number of syllables you'd like on a line
* _alliteration_: `true` or `false`; whether you'd like to see alliteration on a line
* _keyword_: string containing a word you want to see on a line
* _fuzzy_: you want to see a line that happens near a source sentence that has this string keyword.
* _rhyme_: define a rhyme scheme. For example, a couplet template would be:
  `[{"rhyme":"A"}, {"rhyme":"A"}]`
* _blank_: if set to `true`, makes a blank line in the output. for making stanzas.

## example template

    [{"syllables": 10, "keyword": "death", "rhyme": "A"},
     {"syllables": 12, "fuzzy": "death", "rhyme": "B"},
     {"syllables": 10, "rhyme": "A"},
     {"syllables": 10, "rhyme": "B"},
     {"syllables": 8, "fuzzy": "death", "rhyme": "C"},
     {"syllables": 10, "rhyme": "C"}]


## full CLI reference

* `prosaic corpus ls`: list all the databases in your mongo server
* `prosaic corpus rm <database name>`: delete (drop) a corpus
* `prosaic corpus loadfile <filename> -d <dbname>`: add a new file of text to the corpus db specified with `-d`. dbname defaults to `prosaic`
* `prosaic poem new -t <template name> -d <dbname>`: generate a poem using the template specified by `-t` and the corpus db specified by `-d`
* `prosaic template ls`: list the templates prosaic knows about
* `prosaic template rm <template name>`: delete a template
* `prosaic template edit <template name>`: edit existing template using `$EDITOR`
* `prosaic template new <template name>`: write new template using `$EDITOR`
            
## how does prosaic work?

prosaic is two parts: a text parser and a poem writer. a human selects
text files to feed to prosaic, who will chunk the text up into phrases
and tag them with metadata. these phrases all go into a corpus (stored
as a mongodb collection).

once a corpus is prepared, a human then writes (or reuses) a poem
template (in json) that describes a desired poetic structure (number
of lines, rhyme scheme, topic) and provides it to prosaic, who then
uses the
[weltanschauung](http://www.youtube.com/watch?v=L_88FlTzwDE&list=PLD700C5DA258EDD9A)
algorithm to randomly approximate a poem according to the template.

my personal workflow is to build a highly thematic corpus (for
example,
[thirty-one cyberpunk novels](http://cyberpunkprophecies.tumblr.com))
and, for each poem, a custom template. I then run prosaic between five
and twenty times, each time saving and discarding lines or whole
stanzas. finally, I augment the piece with original lines and then
clean up any grammar / pronoun agreement from what prosaic
emitted. the end result is a human-computer collaborative work. you
are, of course, welcome to use prosaic however you see fit.

## changelog

 * 3.4.0 - flurry of improvements to text pre-processing which makes output much cleaner.
 * 3.3.0 - blank rule; can now add blank lines to output for marking stanzas.
 * 3.2.0 - alliteration support!
 * 3.1.0 - can now install prosaic as a command line tool!! also docs!
 * 3.0.0 - lateral port to python (sorry [hy](http://hylang.org)), but there are some breaking naming changes.
 * 2.0.0 - shiny new CLI UI. run `hy __init__.hy -h` to see/explore the subcommands.
 * 1.0.0 - it works

## why mongodb?

MongoDB is almost always the wrong answer to a given architectural
question, but it is particularly well suited for prosaic's needs: no
relational data (and none likely to crop up), no concerns about
HA/consistency, and a well defined document structure.

## further reading

* [Prosaic: A New Approach to Computer Poetry](http://www.amcircus.com/arts/prosaic-a-new-approach-to-computer-poetry.html) by Nathaniel Smith. American Circus, 2013
* [Make poetry from your twitter account!](https://gist.github.com/LynnCo/8447965d98f8b434808e) by [@lynncyrin ](https://twitter.com/lynncyrin)
* [The Cyberpunk Prophecies](http://cyberpunkprophecies.tumblr.com). Cut-up poetry collection made with prosaic using 31 cyberpunk novels.
* [chiptheglasses](http://chiptheglasses.com/tag/poem.html), poetry by Nathaniel Smith, including many prosaic works.
* [Dada Manifesto On Feeble Love And Bitter Love](http://www.391.org/manifestos/1920-dada-manifesto-feeble-love-bitter-love-tristan-tzara.html) by Tristan Tzara, 1920.
* [Prosaic on Gnoetry Daily](https://gnoetrydaily.wordpress.com/tag/prosaic/). Blog of computer poetry featuring some prosaic-generated works.
* [Lovecraft plaintext corpus](https://github.com/nathanielksmith/lovecraftcorpus). Most of H.P. Lovecraft's bibliography in plain text for cutting up.
* [Project Gutenberg](http://www.gutenberg.org/). Lots and lots of public domain books in plaintext.

