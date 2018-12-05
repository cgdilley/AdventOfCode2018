extern crate rust_utils;

fn main() {
    let mut data = rust_utils::files::read_lines("../input/day5.txt")
        .expect("Could not load file.")
        .get_mut(0)
        .expect("Error reading file data.")
        .to_string();

    let result = fuse_string(&mut data);

    println!("The final string is: {}\nIt's length is: {}", result, result.len());
}


fn fuse_string(line: &mut str) -> String {

    let mut chars : Vec<char> = line.chars().collect();

    let mut i = 0;
    while i < chars.len() - 1 {
        let curr = chars.get_mut(i).unwrap().to_string();
        let next = chars.get_mut(i + 1).unwrap().to_string();
        if curr.to_lowercase() == next.to_lowercase() && curr != next {
            chars.remove(i);
            chars.remove(i);
            if i > 0 { i -= 1;}
        }
        else { i += 1; }
    }

    chars.iter().map(|c| c.to_string()).collect()
}
