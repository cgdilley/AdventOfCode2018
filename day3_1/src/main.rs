extern crate rust_utils;
extern crate regex;
#[macro_use] extern crate lazy_static;

use regex::Regex;
use std::collections::HashMap;
use std::collections::HashSet;



fn main() {
    // Read the lines from the file
    let mut data = rust_utils::files::read_lines("../input/day3.txt").expect("Could not load file.");

    let mut rects = build_all_rects(&mut data).expect("Could not parse input");

    let mut aggregation = aggregate(&mut rects);

    let isolated = find_isolated(&mut aggregation);

    println!("These are the IDs of all isolated rects: {:?}", isolated);
}

#[derive(Debug)]
struct Rect {
    id: i32,
    left: i32,
    top: i32,
    width: i32,
    height: i32
}

fn build_rect(line: &mut str) -> Result<Rect, std::num::ParseIntError> {
    lazy_static! {
        static ref RE: Regex = Regex::new(r"^#(\d+) @ (\d+),(\d+): (\d+)x(\d+)").unwrap();
    }

    for capture in RE.captures_iter(line) {
        let r = Rect {
            id: capture[1].parse::<i32>()?,
            left: capture[2].parse::<i32>()?,
            top: capture[3].parse::<i32>()?,
            width: capture[4].parse::<i32>()?,
            height: capture[5].parse::<i32>()?
        };

        return Ok(r);
    }

    panic!();
}

fn build_all_rects(lines: &mut Vec<String>) -> Result<Vec<Rect>, std::num::ParseIntError> {

    let mut rects : Vec<Rect> = Vec::new();

    for line in lines {
        rects.push(build_rect(line)?);
    }

    Ok(rects)
}

fn aggregate(rects: &mut Vec<Rect>) -> HashMap<(i32, i32), Vec<i32>> {

    let mut master = HashMap::new();

    for rect in rects {

        for x in rect.left..(rect.left + rect.width) {
            for y in rect.top..(rect.top + rect.height) {
                let coord = (x, y);
                if !master.contains_key(&coord) {
                    master.insert(coord, Vec::new());
                }
                master.get_mut(&coord).unwrap().push(rect.id);
            }
        }

    }

    master
}


fn find_isolated(aggregation: &mut HashMap<(i32, i32), Vec<i32>>) -> HashSet<&i32> {
    let mut without_overlaps = HashSet::new();
    let mut overlaps = HashSet::new();


    for v in aggregation.values() {
        if v.len() > 1 {
            for id in v {
                overlaps.insert(id);
                without_overlaps.remove(id);
            }
        }
        else {
            if !overlaps.contains(&v[0]) {
                without_overlaps.insert(&v[0]);
            }
        }
    }

    without_overlaps
}