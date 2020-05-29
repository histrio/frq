use std::io::BufReader;
use std::io::BufRead;
use std::fs::File;

use counter::Counter;

fn main() {
    let mut counter: Counter<String> = Counter::new();
    let file = BufReader::new(File::open("cs.tok").expect("Cannot open file.txt"));
    for line in file.lines() {
        for tok in line.unwrap().split_whitespace(){
            if tok.chars().next().unwrap().is_alphabetic() {
                counter[&tok.to_lowercase()] += 1
            }
        }
    }
    for (tok, _) in counter.most_common_ordered().iter().take(5000) {
        println!("{}", tok);
    }
}
