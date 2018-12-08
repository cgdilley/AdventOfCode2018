extern crate rust_utils;

fn main() {
    let mut data = rust_utils::files::read_lines("../input/day8.txt").expect("Could not read file");
    let mut number_strings = data[0].split(' ').collect();
    let mut numbers = convert_to_numbers(&mut number_strings);

    println!("The length of the input is: {}", numbers.len());

    let mut tree = parse_node(&mut numbers);

    println!("{:?}", tree);
}

#[derive(Debug)]
struct Node<'a> {
    child_count: i32,
    meta_count: i32,
    start_index: usize,
    end_index: usize,
    meta: Vec<i32>,
    children: Vec<&'a Node<'a>>
}
impl<'a> Node<'a> {
    fn add_meta(&mut self, v: i32) {
        self.meta.push(v);
    }
    fn add_child(&mut self, c: &'a Node<'a>) {
        self.children.push(c);
    }
}

fn convert_to_numbers(strings: &mut Vec<&str>) -> Vec<i32> {
    return strings.iter().map(|x| x.parse::<i32>().unwrap()).collect();
}

fn parse_node(numbers: &mut Vec<i32>) -> Vec<Node> {

    let mut curr_node : &Node;

    let mut curr_branch : Vec<&mut Node> = Vec::new();
    let mut all_nodes = Vec::new();
    let mut index = 0;


    loop {
        let child_count = *numbers.get(index).unwrap();
        let meta_count = *numbers.get(index + 1).unwrap();
        let n = Node {
            child_count,
            meta_count,
            start_index: index,
            end_index: 0,
            meta: Vec::new(),
            children: Vec::new()
        };
        all_nodes.push(n);
        curr_node = all_nodes.last_mut().unwrap();

        index += 2;
        if curr_branch.len() > 0 {
            curr_branch.last_mut().unwrap().add_child(curr_node);
        }
        curr_branch.push(&mut curr_node);

        let mut done = false;
        loop {
            if curr_branch.len() == 0 {
                done = true;
                break;
            }

            let mut bottom_node : &Node = curr_branch.last_mut().unwrap();
            if bottom_node.child_count != bottom_node.children.len() as i32{
                break;
            }

            for i in 0..meta_count {
                curr_node.add_meta(*numbers.get(index + i as usize).unwrap());
            }

            index += meta_count as usize;
            curr_branch.remove(curr_branch.len() - 1);
        }

        if done { break; }
    }

    all_nodes
}

//fn parse_node(numbers: &mut Vec<i32>, start_index: usize) -> Node {
//
//    let child_count : i32 = *numbers.get(start_index).unwrap();
//    let meta_count : i32 = *numbers.get(start_index + 1).unwrap();
//
//    let mut index = start_index + 2;
//    let mut children = Vec::new();
//    for _ in 0..child_count {
//        let child = parse_node(numbers, index);
//        index = child.end_index+1;
//        children.push(child);
//    }
//
//    let mut meta : Vec<i32> = Vec::new();
//    for i in 0..meta_count {
//        meta.push(*numbers.get(index + i as usize).unwrap())
//    }
//
//    index += meta_count as usize;
//
//    Node {
//        child_count,
//        meta_count,
//        start_index,
//        meta,
//        children,
//        end_index: index
//    }
//}

