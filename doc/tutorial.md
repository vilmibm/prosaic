# prosaic tutorial

## preamble

prosaic is an artistic project created, maintained, and primarily used by one
person. Please forgive any rough edges.

## prerequisites

* linux

prosaic is only thoroughly tested on linux (and debian/ubuntu, at that). There
is nothing I know of that would keep it from working on OS X. It does not work
on windows.

* build tools

Some of prosaic's python dependencies require native compilation. You'll want the packages that provide this installed on your system (like python3-dev packages, build-essential, gcc...)

* python 3.5.1

prosaic only works with Python 3.5+.

* Postgresql 9+

prosaic stores cut-up phrases in postgresql.

### setting up the database

The following is a rough crash course in setting up the database where prosaic
will store text metadata. You'll end up with a database called `prosaic` owned
by a user `prosaic` with password `prosaic`. You are of course welcome to use
different credentials; see the section on the configuration file for how to
point prosaic at a different database set up.

```bash
# install postgresql, i.e. `sudo apt install postgresql`
sudo su - postgres
create user prosaic -P
# enter 'prosaic' as the password
createdb prosaic -O prosaic
# to confirm it's working:
psql prosaic -h127.0.0.1 -dprosaic
# if it connects without issue, prosaic will be good to go.
```

### getting some text

I recommend checking out [project gutenberg](http://gutenberg.org) for books to
play around with. I further recommend manually stripping all of the header and
footer text from the books' text files before giving them to prosaic (as marked
with "BEGINNING OF PROJECT GUTENBERG BOOK..." and "END OF PROJECT GUTENBERG
BOOK...").

I also maintain a [corpus of Lovecraft
works](https://github.com/nathanielksmith/lovecraftcorpus) in plaintext, all of
which are in the public domain.

### adding some sources

A `source` is a unit of text--like a book or the text of a web page--that you
want to ultimately generate poetry from, potentially mixing with other sources.

Add them like so:

```bash
prosaic source new pride_and_prejudice /path/to/pride_and_prejudice.txt
prosaic source new call_of_cthulhu /path/to/call_of_cthulhu.txt
```

Each source is given a name. You can see what sources you have with `source ls`:

```bash
prosaic source ls

pride_and_prejudice
call_of_cthulhu
```

### making a corpus

Corpora are combinations of sources. We use them to generate poetry. We'll need
to add any sources we want to use to a corpora before we can generate poetry
from them.

```bash
prosaic corpus new pride_and_cthulhu
prosaic corpus link pride_and_cthulhu pride_and_prejudice
prosaic corpus link pride_and_cthulhu call_of_cthulhu
```

Now we have a corpus called `pride_and_cthulhu` and it has two sources. We can
make sure this worked with:

```bash
prosaic corpus sources pride_and_cthulhu

pride_and_prejudice
call_of_cthulhu
```

### writing a template

We want to make a simple, six line poem with some keywords, a little
alliteration, and some rhyming. Running the following command will drop you into the program you have set as $EDITOR.

```bash
export EDITOR=$(which vim) # optionally set us up to use vim
prosaic template new simple
```

Fill in the template as so, being careful with your commas and double quotes:

```json
[
  {"keyword": "dark", "syllables": 10, "alliteration": true},
  {"rhyme": "A", "fuzzy": "deep", "syllables": 8},
  {"rhyme": "A", "fuzzy": "parlor", "syllables": 10},
  {"blank": "true"},
  {"keyword": "sleep", "syllables": 9, "alliteration": true},
  {"rhyme": "B", "syllables": 6},
  {"rhyme": "B", "syllables": 8}
]
```

Save the file. You can now use the `simple` template to generate a poem.

### generating a poem

Now that we have made sources, put them in a corpus, and written a template, we can generate a poem (yay).

```bash
prosaic poem new -t simple -c pride_and_cthulhu

idols brought in dim eras from dark stars.
"Your picture may be very exact, Louisa," said Bingley
I desire you will do no such thing.

Mr. Hurst had therefore nothing to do
Of this she was perfectly unaware
Oh!
```

Congratulations; you, jane austen, cthulhu, and your computer just wrote a poem
together.

### configuration file

You can change the database connection details in `~/.prosaic/prosaic.conf`. The default config looks like this:

```hocon
database: {
    user: prosaic
    password: prosaic
    host: 127.0.0.1
    port: 5432
    dbname: prosaic
}
default_template: haiku
```

Update as needed with your postgresql details. you can also change what template is used when `prosaic poem new` is run without the `-t` argument.
