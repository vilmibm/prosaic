use std::io;
use std::env;
use std::process;

use serde_json::json;


fn to_jsonl(source_name: &String, phrase_buff: String) -> String {
    json!({
        "source": source_name,
        "raw": phrase_buff,
    }).to_string()
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("need exactly one argument, a source name (got {})", args.len());
        process::exit(1);
    }

    let source_name = &args[1];
    let mut phrase_buff = String::from("");

    for line in io::stdin().lines() {
        for c in line.unwrap().chars() {
            if c == ';' || c == ',' || c == ':' || c == '.' || c == '?' || c == '!' {
                if phrase_buff.len() >= 20 {
                    println!("{}", to_jsonl(source_name, phrase_buff))
                }
                phrase_buff = String::from("");
                // TODO check phrase_buff len
                // TODO print jsonl or not
                // TODO reset phrase buff
            } else {
                phrase_buff.push(c);
            }
        }
    }

}
