                                   o
           _   ,_    __   ,   __,      __
         |/ \_/  |  /  \_/ \_/  |  |  /
         |__/    |_/\__/  \/ \_/|_/|_/\___/
        /|
        \|

# prosaic

being a prose scraper & cut-up poetry generator

by [nathanielksmith](https://tilde.town/~vilmibm)

using [nltk](http://nltk.org)

and licensed under the [GPL](https://www.gnu.org/copyleft/gpl.html).

## what is prosaic?

prosaic is a tool for
[cutting up](https://en.wikipedia.org/wiki/Cut-up_technique) large quantities of
text and rearranging it to form poetic works.

## prerequisites

* postgresql 9.0+
* python 3.5+
* linux (it probably works on a mac, i donno)
* you might need some -dev libraries and/or gcc to get nltk to compile

## database setup

Prosaic requires a postgresql database. Once you've got postgresql installed,
run the following to create a database prosaic can access (assumes you're on
linux; refer to google to perform steps like this on osx/windows):

    sudo su postgres
    createuser prosaic -P
    # at password prompt, type prosaic and hit enter
    createdb prosaic -O prosaic

## quick start

    sudo pip install prosaic
    prosaic source new pride_and_prejudice pandp.txt
    prosaic source new hackers hackers_screenplay.txt
    prosaic corpus new pride_and_hackers
    prosaic corpus link pride_and_hackers pride_and_prejudice
    prosaic corpus link pride_and_hackers hackers
    prosaic poem new -cpride_and_hackers -thaiku

    and so I warn you.
    We will know where we have gone
    ALL: HACK THE PLANET

See the [full tutorial](doc/tutorial.md) for more detailed instruction. There
is also a [cli reference](doc/cli.md).

## use as a library

This is a little complex right now; I'm working on a simpler API.

```python
from io import StringIO
from prosaic.cfg import DEFAULT_DB
from prosaic.models import Database, Source, Corpus, get_session
from prosaic.parsing import process_text
from prosaic.generate import poem_from_template

db = Database(**DEFAULT_DB)

source = Source(name='some_name')
process_text(db, source, StringIO('some very long string of text')

session = get_session(db)
corpus = Corpus(name='sweet corpus', sources=[source])
session.add(corpus)
session.commit()

# poem_from_template returns raw line dictionaries from the database:
poem_lines = poem_from_template([{'syllables': 5}, {'syllables':7}, {'syllables':5}], 
                                db,
                                corpus.id)

# pull raw text out of each line dictionary and print it:
for line in poem_lines:
  print(line[0])
```

## use on the web

there is an *extremely alpha* web wrapper (currently being re-written) at
[prosaic.party](https://prosaic.party).

## write a template

Templates are currently stored as json files (or passed from within code as
python dictionaries) that represent an array of json objects, each one
containing describing a line of poetry.

A template describes a "desired" poem. Prosaic uses the template to approximate
a piece given what text it has in its database. Running prosaic repeatedly with
the same template will almost always yield different results.

You can see available templates with `prosaic template ls`, edit them with
`prosaic template edit <template name>`, and add your own with `prosaic
template new <template name>`.

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

Check out [the CLI reference documentation](./doc/cli.md).
            
## how does prosaic work?

prosaic is two parts: a text parser and a poem writer. a human selects
text files to feed to prosaic, who will chunk the text up into phrases
and tag them with metadata. the human then links each of these parsed text
files to a corpus.

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

## developing

Patches are more than welcome if they come with tests. Tests should always be
green in master; if not, please let me know! To run the tests:

```bash
# assuming you have pip install'd prosaic from source into an activated venv:
cd test
py.test
```

## changelog

 * 6.1.1

  * fix error handling; this was preventing sources from being made.

 * 6.1.0

  * default to a system-wide nltk\_data directory; won't download and install to
    `~` if found. the path is `/usr/share/nltk_data`. this is probably only
    useful on systems where prosaic is installed globally for multiple users
    (like on [tilde.town](https://tilde.town)).
  * not tied to a release, but the readme has database setup instructions now.

 * 6.0.0

  * I guess I forgot to change-log 5.x, oops
  * process_text now takes a read()able thing instead of a string and a database
    config object as first param
  * parsing is faster but at the expense of less precision
  * slightly saner DB engine handling

 * 4.0.0

  * Port to postgresql + sqlalchemy
  * Completely rewrite command line interface
  * Add a --verbose flag and muzzle the logging that used to happen
    unless it's present
  * Support a configuration file (~/.prosaic/prosaic.conf) for
    specifying database connections and default template
  * Rename some modules
  * Remove some vestigial features

 * 3.5.4 - update nltk dependence so prosaic works on python 3.5
 * 3.5.3 - mysterious release i don't know
 * 3.5.2 - handle weird double escaping issues
 * 3.5.1 - fix stupid typo
 * 3.5.0 - prosaic now respects environment variables PROSAIC\_DBNAME, PROSAIC\_DBPORT and PROSAIC\_DBHOST. These are used if not overriden from the command line. If neither environment variables nor CLI args are provided, static defaults are used (these are unchanged).
 * 3.4.0 - flurry of improvements to text pre-processing which makes output much cleaner.
 * 3.3.0 - blank rule; can now add blank lines to output for marking stanzas.
 * 3.2.0 - alliteration support!
 * 3.1.0 - can now install prosaic as a command line tool!! also docs!
 * 3.0.0 - lateral port to python (sorry [hy](http://hylang.org)), but there are some breaking naming changes.
 * 2.0.0 - shiny new CLI UI. run `hy __init__.hy -h` to see/explore the subcommands.
 * 1.0.0 - it works

## further reading

* [Prosaic: A New Approach to Computer Poetry](http://www.amcircus.com/arts/prosaic-a-new-approach-to-computer-poetry.html) by Nathaniel Smith. American Circus, 2013
* [The Cyberpunk Prophecies](http://cyberpunkprophecies.tumblr.com). Cut-up poetry collection made with prosaic using 31 cyberpunk novels.
* [graveyard theory](http://graveyardtheory.net/tag/poem.html), poetry by Nathaniel Smith, including many prosaic works.
* [Make poetry from your twitter account!](https://gist.github.com/LynnCo/8447965d98f8b434808e) by [@lynncyrin ](https://twitter.com/lynncyrin)
* [Dada Manifesto On Feeble Love And Bitter Love](http://www.391.org/manifestos/1920-dada-manifesto-feeble-love-bitter-love-tristan-tzara.html) by Tristan Tzara, 1920.
* [Prosaic on Gnoetry Daily](https://gnoetrydaily.wordpress.com/tag/prosaic/). Blog of computer poetry featuring some prosaic-generated works.
* [Lovecraft plaintext corpus](https://github.com/nathanielksmith/lovecraftcorpus). Most of H.P. Lovecraft's bibliography in plain text for cutting up.
* [Project Gutenberg](http://www.gutenberg.org/). Lots and lots of public domain books in plaintext.

