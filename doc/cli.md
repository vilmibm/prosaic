# prosaic cli interface

All subcommands are passed to the `prosaic` command:

    prosaic poem new

# Standard arguments

* -v, --verbose: Log actions and errors to STDERR
* -V, --version: Prints prosaic's version and exits
* -h, --help: Display help information
* -d, --dbname: Database name. Defaults to `prosaic`
* -p, --port: Database port. Defaults to `5432`
* -w, --password: Database password. Defaults to `prosaic`
* -o, --host: Database host. Defaults to `localhost`
* -u, --user: Database user. Defaults to `prosaic`

# subcommands

## corpus

_aliases_: c, corpora

* ls
* rm
* new
* link
* unlink

### ls

    prosaic corpus ls

List all of the corpora prosaic knows about.

### rm

    prosaic corpus rm "corpus name"

Delete a corpus and unlink it from any sources.

### new

    prosaic corpus new "corpus name" ["corpus description"]

Create a new, empty corpus. Optionally accepts a description for the corpus.

### link

    prosaic corpus link "corpus name" "source name"

Adds a source to a given corpus.

### unlink

    prosaic corpus unlink "source name"

Removes a source from a given corpus.

## source

_aliases_: s, sources

* ls
* rm
* new

### ls

    prosaic source ls

Lists all of the sources (ie files of text) that prosaick knows about.

### rm

    prosaic source rm "source name"

Delete a source, unlinking it from any corpora.

### new 

    prosaic source new "source name" "path to txt file" ["description"]

Create a new source from a given file path. Prosaic will read the file, parse
its sentences, and save them. Optionally, provide a description for the source.

The sentences from the source are unavailable for use in poems until the source
is linked to a corpora.

## poem

_aliases: p

* new

### new

    prosaic poem new [-t "template name" -c "corpus name" -o "file name"]

* -c, --corpus: Specify which corpus to use. If left out, uses all phrases prosaic knows of.
* -t, --template: Specify what template to use. If left out, uses `haiku`.
* -o, --output: Optionally specify a file to save the poem in. If left out, prints to STDOUT. 

Generate a new poem.

## template

_aliases_: t, tmpl

* ls
* rm
* new
* edit

### ls

    prosaic template ls

List all templates prosaic knows about.

### rm

    prosaic template rm "template name"

Remove a template from the disk.

### new 

    prosaic template new "template name"

Create a new template using $EDITOR.

### edit

    prosaic template edit "template name"
 
Edit a template using $EDITOR. If it does not exist, it will be created.

