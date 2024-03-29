use std::io;
use std::process;

use clap::Parser;

use cmudict_fast::Cmudict;
use std::str::FromStr;
use serde_json::json;
use rust_stemmers::{Algorithm,Stemmer};

struct Analyzer {
    cmudict: Cmudict,
    stemmer: Stemmer,
    source_name: String,
}

#[derive(Parser)]
struct PhraserArgs {
    #[arg(long)]
    json: bool,
    #[arg(long)]
    name: Option<String>,
}

impl Analyzer {
    fn to_jsonl(&self, phrase_buff: String) -> String {
        // TODO idea: before emitting a phrase jsonl, QA it. is it mostly non alphanumeric?
        let words = phrase_buff.split_whitespace();
        let mut phonemes:  Vec<String> = vec![];
        let mut stems: Vec<String> = vec![];
        for w in words {
            let ww = String::from_str(w).unwrap().to_lowercase();
            let www: &str = &ww;
            let stemmed = self.stemmer.stem(www);
            stems.push(stemmed.to_string());
            match self.cmudict.get(www) {
                Some(rule) => {
                    match rule.first() {
                        Some(r) => {
                            for s in r.pronunciation() {
                                phonemes.push(s.to_string());
                            }
                        }
                        None => ()
                    }
                },
                None => (),
            }
        }
        json!({
            "source": self.source_name,
            "raw": phrase_buff.trim(),
            "phonemes": phonemes,
            "stems": stems,
        }).to_string()
    }
}

// TODO syllable count
// TODO decide if i want the bad character filtering
//      from parsing.py: '\n', '|', '/', '\\', '#', '_'
// TODO see if i want \n detection; right now those are lost

fn main() {
    let args = PhraserArgs::parse();
    let source_name = match args.name {
        Some(n) => n,
        None => String::from(""),
    };

    if args.json && source_name == "" {
        eprintln!("--name required when --json");
        process::exit(1)
    }

    // TODO consider using a hashset
    let phrase_markers = [
        ';', ',', ':', '.', '?', '!', '(', ')', '"', '{', '}', '[', ']',
        '“', '”', '=', '`',
    ];

    // TODO avoid this setup if in raw mode
    let cmudict_raw = include_str!("cmudict.dict");
    let cmudict = Cmudict::from_str(cmudict_raw).unwrap();
    let stemmer = Stemmer::create(Algorithm::English);
    let a = Analyzer{
        cmudict, stemmer,
        source_name: source_name.clone(),
    };
    let mut phrase_buff = String::from("");

    // TODO the too-long check; if phrase_buff len is over some arbitrary value and we see
    // something like ' ' then just cut it off there. can help with pathologic stuff.
    // TODO think about '
    // TODO think about . not ending a sentence

    for line in io::stdin().lines() {
        for c in line.unwrap().chars() {
            if phrase_markers.iter().any(|ch| *ch == c) {
                if phrase_buff.len() >= 20 && phrase_buff.contains(' ') {
                    if args.json {
                        println!("{}", a.to_jsonl(phrase_buff))
                    } else {
                        println!("{}", phrase_buff.trim());
                    }
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
