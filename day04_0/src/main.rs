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
    // This maps guard ids to counts of the total number of minutes spent asleep
    let mut minutes_by_id = HashMap::new();

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
            // If this event is a wake command, find the time difference and add it
            // to the guard's total sleep amount
            let time_diff = &event.minute - sleep_time;
            let counter = minutes_by_id.entry(&event.id).or_insert(0);
            *counter += time_diff;

            // Then iterate through all minutes in the sleeping span, and increase
            // the asleep counter for those minutes for this guard
            for min in *sleep_time..event.minute {
                let entry = asleep_minutes_by_id.entry(&event.id).or_insert(HashMap::new());
                let min_count = entry.entry(min).or_insert(0);
                *min_count += 1;
            }
        }
    }

    // Identify the guard that slept the most
    let mut max = (0, 0);
    for kvp in minutes_by_id {
        if kvp.1 > max.1 {
            max = (*kvp.0, kvp.1);
        }
    }
    println!("The guard with the most minutes is #{}, with {} minutes asleep.",
                max.0, max.1);

    // Identify the particular minute on which the above-found guard slept the most
    let mut max_minute = (0, 0);
    for kvp in asleep_minutes_by_id.get_mut(&max.0).unwrap() {
        if *kvp.1 > max_minute.1 {
            max_minute = (*kvp.0, *kvp.1);
        }
    }

    println!("The guard slept the most on minute {} ({} times)",
             max_minute.0,
             max_minute.1);

    println!("The solution to problem 1 is: {}", max_minute.0 * max.0)
}