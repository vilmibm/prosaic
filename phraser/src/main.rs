use std::io;
use std::env;
use std::process;

use cmudict_fast::Cmudict;
use std::str::FromStr;
use serde_json::json;
use rust_stemmers::{Algorithm,Stemmer};

struct Analyzer {
    cmudict: Cmudict,
    stemmer: Stemmer,
    source_name: String,
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
// TODO research advancements in programmatic scansion
// TODO decide if i want the bad character filtering
//      from parsing.py: '\n', '|', '/', '\\', '#', '_'
// TODO see if i want \n detection; right now those are lost
// TODO include cmudict copyright notice somewhere (Copyright (c) 2015, Alexander Rudnicky)

fn main() {
    // TODO raw mode that just prints phrases and not jsonl
    // TODO consider using a hashset
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
                    println!("{}", a.to_jsonl(phrase_buff))
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
