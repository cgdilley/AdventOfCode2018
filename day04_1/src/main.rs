extern crate rust_utils;
extern crate regex;
#[macro_use]
extern crate lazy_static;

use regex::Regex;
use std::collections::HashMap;


fn main() {
    let mut data = rust_utils::files::read_lines("../input/day4.txt")
        .expect("Could not load data from file.");

    data.sort();

    let mut events = process_events(&mut data)
        .expect("Could not process events.");

    collect_sleep_times(&mut events);
}

#[derive(Debug)]
struct ShiftEvent {
    id: i32,
    month: i32,
    day: i32,
    hour: i32,
    minute: i32,
    command: String,
}


fn process_events(event_strings: &mut Vec<String>) -> Result<Vec<ShiftEvent>, std::num::ParseIntError> {
    lazy_static! {
        static ref RE_EVENT: Regex = Regex::new(r"^\[\d{4}-(\d{2})-(\d{2}) (\d{2}):(\d{2})] (.*)$").unwrap();
    }
    lazy_static! {
        static ref RE_COMMAND: Regex = Regex::new(r"^Guard #(\d+) begins shift$").unwrap();
    }

    let mut events = Vec::new();
    let mut curr_id = 0;
    for event in event_strings {
        let caps = RE_EVENT.captures(event).unwrap();
        let mut command: &str = &caps[5];
        // Attempt to parse the command as if it were a shift change.
        // If successful, update the current ID and add the "begin" command.
        // Otherwise, parse the command either as a "sleep" or "wake" command.
        match RE_COMMAND.captures(command) {
            Some(sub_caps) => {
                curr_id = sub_caps[1].parse::<i32>()?;
                command = "begin";
            }
            None => {
                if command.starts_with("falls") {
                    command = "sleep";
                } else {
                    command = "wake";
                }
            }
        }

        let e = ShiftEvent {
            id: curr_id,
            month: caps[1].parse::<i32>()?,
            day: caps[2].parse::<i32>()?,
            hour: caps[3].parse::<i32>()?,
            minute: caps[4].parse::<i32>()?,
            command: command.to_string(),
        };

        events.push(e);
    }

    Ok(events)
}

fn collect_sleep_times(events: &mut Vec<ShiftEvent>) {

    // This maps guard ids to another map that maps particular minutes to the total number
    // of times the guard was asleep on that particular minute.
    let mut asleep_minutes_by_id = HashMap::new();

    // Keeps track of the time at which the last sleep command was given
    let mut sleep_time = &0;

    // Reads through all of the events
    for event in events {

        // If this event is a sleep command, mark the beginning of the sleep
        if event.command == "sleep" {
            sleep_time = &event.minute;
        } else if event.command == "wake" {

            // Then iterate through all minutes in the sleeping span, and increase
            // the asleep counter for those minutes for this guard
            for min in *sleep_time..event.minute {
                let entry = asleep_minutes_by_id.entry(&event.id).or_insert(HashMap::new());
                let min_count = entry.entry(min).or_insert(0);
                *min_count += 1;
            }
        }
    }

    // Find the minute at which a particular guard is asleep most often,
    // and additionally note the ID of the guard and the relevant minute
    let mut max_amount = 0;
    let mut id_of_max = &0;
    let mut minute_of_max = 0;
    for id in asleep_minutes_by_id {
        for kvp in id.1 {
            if kvp.1 > max_amount {
                max_amount = kvp.1;
                id_of_max = id.0;
                minute_of_max = kvp.0;
            }
        }
    }

    println!("Guard #{} slept the most on a particular minute.  On minute {}, this guard \
               slept {} times.\nThe solution to problem 2 is: {}",
             id_of_max,
             minute_of_max,
             max_amount,
             id_of_max * minute_of_max);
}