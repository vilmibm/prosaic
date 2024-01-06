use std::io;

fn main() {
    // TODO source name argument
    for line in io::stdin().lines() {
        println!("LINE {}", line.unwrap());
    }

    // TODO
}
