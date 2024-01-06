use std::io;
use std::env;
use std::process;

use serde_json::json;


// TODO stemming
// TODO syllable count
// TODO phonemes
// TODO research advancements in programmatic scansion
// TODO decide if i want the bad character filtering
//      from parsing.py: '\n', '|', '/', '\\', '#', '_'
// TODO see if i want \n detection; right now those are lost

fn to_jsonl(source_name: &String, phrase_buff: String) -> String {
    // TODO trim whitespace
    json!({
        "source": source_name,
        "raw": phrase_buff.trim(),
    }).to_string()
}

fn main() {
    // TODO consider just putting this in a string and using contains or using a hashset but this
    // is already dumb fast
    let phrase_markers = [
        ';', ',', ':', '.', '?', '!', '(', ')', '"', '{', '}', '[', ']',
        '“', '”', '=', '`',
    ];
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("need exactly one argument, a source name (got {})", args.len());
        process::exit(1);
    }

    let source_name = &args[1];
    let mut phrase_buff = String::from("");

    // TODO the too-long check; if phrase_buff len is over some arbitrary value and we see
    // something like ' ' then just cut it off there. can help with pathologic stuff.
    // TODO think about '
    // TODO think about . not ending a sentence

    for line in io::stdin().lines() {
        for c in line.unwrap().chars() {
            if phrase_markers.iter().any(|ch| *ch == c) {
                if phrase_buff.len() >= 20 && phrase_buff.contains(' ') {
                    println!("{}", to_jsonl(source_name, phrase_buff))
                }
                phrase_buff = String::from("");
            } else {
                if c == ' ' && phrase_buff.ends_with(' ') {
                    continue
                }
                phrase_buff.push(c);
            }
        }
    }

}
