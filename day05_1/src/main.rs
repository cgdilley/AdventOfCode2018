extern crate rust_utils;
extern crate regex;

use std::collections::HashSet;
use regex::Regex;

fn main() {
    let mut data = rust_utils::files::read_lines("../input/day5.txt")
        .expect("Could not load file.")
        .get_mut(0)
        .expect("Error reading file data.")
        .to_string();


    let result = test_all_removals(&mut data);

    println!("The shortest result is obtained by removing {}{}, resulting in: {}\nThis result has a length of: {}",
             result.0, result.0.to_uppercase(),
             result.1,
             result.1.len());
}

fn get_unique_chars(line: &mut str) -> HashSet<String> {
    let mut set = HashSet::new();

    for ch in line.chars() {
        set.insert(ch.to_string().to_lowercase());
    }

    set
}

fn test_all_removals(line: &mut str) -> (String, String) {
    let set = get_unique_chars(line);

    let mut min = ("".to_string(), "".to_string());
    for ch in set {
        let re = Regex::new(&format!("[{}{}]", ch, ch.to_uppercase())).unwrap();

        let mut new_line = re.replace_all(line, "").to_string();
        let fused = fuse_string(&mut new_line);

        if min.1.len() == 0 || fused.len() < min.1.len() {
            min = (ch, fused);
        }
    }

    min
}

fn fuse_string(line: &mut str) -> String {
    let mut chars: Vec<char> = line.chars().collect();

    let mut i = 0;
    while i < chars.len() - 1 {
        let curr = chars.get_mut(i).unwrap().to_string();
        let next = chars.get_mut(i + 1).unwrap().to_string();
        if curr.to_lowercase() == next.to_lowercase() && curr != next {
            chars.remove(i);
            chars.remove(i);
            if i > 0 { i -= 1; }
        } else { i += 1; }
    }

    chars.iter().map(|c| c.to_string()).collect()
}
