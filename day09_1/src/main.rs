extern crate rust_utils;
extern crate regex;

use regex::Regex;
use std::collections::HashMap;

fn main() {
    let input = rust_utils::files::read_lines("../input/day9.txt").expect("Could not read file.");
    let processed = Regex::new(r"^(\d+)[^\d]+(\d+)").unwrap().captures(&input[0]).unwrap();
    let players = processed[1].parse::<i32>().unwrap();
    let marbles = (processed[2].parse::<i32>().unwrap() * 100) + 1;

    println!("{} player, {} marbles", players, marbles);

    let results = play_game(&players, &marbles);

    let high_score = results.values().into_iter().max().unwrap();

    println!("The highest score is: {}", high_score);
}


fn play_game(players: &i32, marbles: &i32) -> HashMap<i32, i32> {

    let mut game_state = Vec::new();
    let mut scores = initialize_scores(&players);
    let mut index : usize = 0;
    let mut curr_player = 0;

    game_state.push(0);

    for marble in 1..*marbles {

        if is_scoring_marble(&marble) {
            let removal_index = bind_index(&(index as i32 - 7), &game_state);
            let score = marble + game_state[removal_index];

            *scores.get_mut(&curr_player).unwrap() += score;
            game_state.remove(removal_index);
            index = removal_index;

//            println!("Player {} scores {} points!", curr_player, score);
        }
        else {
            let insert_index = bind_index(&(index as i32 + 2), &game_state);
            game_state.insert(insert_index, marble);
            index = insert_index;
        }
        curr_player += 1;
        if curr_player >= *players {
            curr_player = 0;
        }

        if marble % 100000 == 0 {
            println!("Played {} marbles...", marble);
        }
    }

    scores

}

fn bind_index<T>(index: &i32, vec: &Vec<T>) -> usize {
    let len = vec.len() as i32;
    if len == 0 {
        return 0;
    }

    let mut i = *index;
    while i < 0 {
        i += len;
    }
    while i >= len {
        i -= len
    }

    i as usize
}

fn is_scoring_marble(marble: &i32) -> bool {
    *marble % 23 == 0
}

fn initialize_scores(players: &i32) -> HashMap<i32, i32> {
    let mut map = HashMap::new();
    for p in 0..*players {
        map.insert(p, 0);
    }
    map
}