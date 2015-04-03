                                   o
           _   ,_    __   ,   __,      __
         |/ \_/  |  /  \_/ \_/  |  |  /
         |__/    |_/\__/  \/ \_/|_/|_/\___/
        /|
        \|

## prosaic

being a prose scraper & poetry generator

by [nathanielksmith](http://chiptheglasses.com)

written in [hy](http://hylang.org)

using [nltk](http://nltk.org)

(formerly written with
[nodejs](https://github.com/nathanielksmith/node-prosaic))

and licensed under the [GPL](https://www.gnu.org/copyleft/gpl.html).

## notes

the setup.py works, but beware that you still have to manually run the hy \_\_init\_\_.hy script. The workflow I use is:

 * install python-dev(el), whatever makes sense for your platform
 * clone this repo
 * virtualenv ~/prosaic -p $(which python3)
 * source ~/prosaic/bin/activate
 * cd prosaic && pip install .
 * cd prosaic (into the source code, not the venv) and run the below commands

(obviously you are welcome to put the venv wherever).

        hy __init__.hy corpus loadfile -d some_mongo_db_name some_file0.txt
        hy __init__.hy corpus loadfile -d some_mongo_db_name some_file1.txt
        hy __init__.hy corpus loadfile -d some_mongo_db_name some_file2.txt

        hy __init__.hy poem new -t haiku -d some_mongo_db_name

one can also do this programmatically from either python (you'll need
to compile all of the hy with hyc first) or hy; import
`prosaic.cthulhu.poem-from-template` to create poems or
`prosaic.nyarlathotep.process-text!` to parse text and make
corpora. There are no docs. read the source or look at `cthtest.hy`
for some example usage.

## working with templates

a few sample poem templates are included with `prosaic`. you can check them out with `hy __init__.hy template ls` and then `hy __init__.hy template edit <template name>`. make your own with `hy __init__.hy template new <template name>`. templates are stored in `~/.prosaic`.

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

 * 2.0.0 - shiny new CLI UI. run `hy __init__.hy -h` to see/explore the subcommands.
 * 1.0.0 - it works

### why hy?

I am returning to the world of Python after a long and strange sojourn
that included a lot of Clojure. I love Python and the Python community
but my brain thinks in s expressions, now. I find Hy to be useful,
fun, and highly compatible with my brain.

### why mongodb?

MongoDB is almost always the wrong answer to a given architectural
question, but it is particularly well suited for prosaic's needs: no
relational data (and none likely to crop up), no concerns about
HA/consistency, and a well defined document structure.
