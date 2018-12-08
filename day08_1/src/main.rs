extern crate rust_utils;

fn main() {
    let data = rust_utils::files::read_lines("../input/day8.txt").expect("Could not read file");
    let mut number_strings = data[0].split(' ').collect();
    let mut numbers = convert_to_numbers(&mut number_strings);

    println!("The length of the input is: {}", numbers.len());

    let mut root = parse_node(&mut numbers, 0);

    let val = get_value(&mut root);

    println!("The value of the root node is: {}", val);
}

#[derive(Debug)]
struct Node {
    child_count: i32,
    meta_count: i32,
    start_index: usize,
    end_index: usize,
    meta: Vec<i32>,
    children: Vec<Node>,
}

fn convert_to_numbers(strings: &mut Vec<&str>) -> Vec<i32> {
    return strings.iter().map(|x| x.parse::<i32>().unwrap()).collect();
}


fn parse_node(numbers: &mut Vec<i32>, start_index: usize) -> Node {
    let child_count: i32 = *numbers.get(start_index).unwrap();
    let meta_count: i32 = *numbers.get(start_index + 1).unwrap();

    let mut index = start_index + 2;
    let mut children = Vec::new();
    for _ in 0..child_count {
        let child = parse_node(numbers, index);
        index = child.end_index;
        children.push(child);
    }

    let mut meta: Vec<i32> = Vec::new();
    for i in 0..meta_count {
        meta.push(*numbers.get(index + i as usize).unwrap())
    }

    index += meta_count as usize;

    Node {
        child_count,
        meta_count,
        start_index,
        meta,
        children,
        end_index: index,
    }
}

fn get_value(node: &mut Node) -> i32 {
    if node.child_count == 0 {
        return node.meta.iter().sum::<i32>();
    }

    let mut val = 0;
    for meta in &node.meta {
        if *meta - 1 < node.child_count {
            val += get_value(node.children.get_mut(*meta as usize - 1).unwrap());
        }
    }

    val
}
