                                   o
           _   ,_    __   ,   __,      __
         |/ \_/  |  /  \_/ \_/  |  |  /
         |__/    |_/\__/  \/ \_/|_/|_/\___/
        /|
        \|

## prosaic

being a prose scraper & poetry generator

by [nathanielksmith](http://chiptheglasses.com)

using [nltk](http://nltk.org)

and licensed under the [GPL](https://www.gnu.org/copyleft/gpl.html).

## notes

the setup.py works, but i haven't put it on pypi yet / set up entry points. my workflow:

 * install python-dev(el), whatever makes sense for your platform
 * clone this repo
 * virtualenv ~/prosaic -p $(which python3)
 * source ~/prosaic/bin/activate
 * cd prosaic && pip install .
 * cd prosaic (into the source code, not the venv) and run the below commands

(obviously you are welcome to put the venv wherever).

        python __init__.py corpus loadfile -d some_mongo_db_name some_file0.txt
        python __init__.py corpus loadfile -d some_mongo_db_name some_file1.txt
        python __init__.py corpus loadfile -d some_mongo_db_name some_file2.txt

        python __init__.py poem new -t haiku -d some_mongo_db_name

one can also do this programmatically from either python. Import
`prosaic.cthulhu.poem_from_template` to create poems or
`prosaic.nyarlathotep.process_text` to parse text and make
corpora. There are no docs, yet, and i'm sorry.

## working with templates

a few sample poem templates are included with `prosaic`. you can check them out with `python __init__.py template ls` and then `python __init__.py template edit <template name>`. make your own with `python __init__.py template new <template name>`. templates are stored in `~/.prosaic`.

### how does prosaic work?

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

### changelog

 * 3.0.0 - lateral port to python (sorry [hy](http://hylang.org)), but there are some breaking naming changes.
 * 2.0.0 - shiny new CLI UI. run `hy __init__.hy -h` to see/explore the subcommands.
 * 1.0.0 - it works

### why mongodb?

MongoDB is almost always the wrong answer to a given architectural
question, but it is particularly well suited for prosaic's needs: no
relational data (and none likely to crop up), no concerns about
HA/consistency, and a well defined document structure.
