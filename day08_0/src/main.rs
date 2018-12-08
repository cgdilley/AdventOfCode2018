extern crate rust_utils;

fn main() {
    let data = rust_utils::files::read_lines("../input/day8.txt").expect("Could not read file");
    let mut number_strings = data[0].split(' ').collect();
    let mut numbers = convert_to_numbers(&mut number_strings);

    println!("The length of the input is: {}", numbers.len());

    let root = parse_node(&mut numbers, 0);

    let mut nodes = collect_nodes(&root);

    let sum = sum_nodes(&mut nodes);

    println!("The sum of all metadata values is: {}", sum);
}

#[derive(Debug)]
struct Node {
    child_count: i32,
    meta_count: i32,
    start_index: usize,
    end_index: usize,
    meta: Vec<i32>,
    children: Vec<Node>
}

fn convert_to_numbers(strings: &mut Vec<&str>) -> Vec<i32> {
    return strings.iter().map(|x| x.parse::<i32>().unwrap()).collect();
}


fn parse_node(numbers: &mut Vec<i32>, start_index: usize) -> Node {

    let child_count : i32 = *numbers.get(start_index).unwrap();
    let meta_count : i32 = *numbers.get(start_index + 1).unwrap();

    let mut index = start_index + 2;
    let mut children = Vec::new();
    for _ in 0..child_count {
        let child = parse_node(numbers, index);
        index = child.end_index;
        children.push(child);
    }

    let mut meta : Vec<i32> = Vec::new();
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
        end_index: index
    }
}

fn collect_nodes(root: &Node) -> Vec<&Node> {

    let mut nodes = Vec::new();

    nodes.push(root);

    for child in &root.children {
        nodes.append(collect_nodes(child).as_mut())
    }

    return nodes;

}

fn sum_nodes(nodes: &mut Vec<&Node>) -> i32
{
    let mut s = 0;

    for node in nodes {
        s += (*node).meta.iter().sum::<i32>();
    }

    s
}
