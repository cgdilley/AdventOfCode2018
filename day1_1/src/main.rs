use std::fs::File;
use std::io;
use std::io::prelude::*;
use std::collections::HashSet;


fn main() {
    // Read the lines from the file
    let mut data = read_lines("../input/day1.txt").expect("Could not load file.");

    // Convert the lines into integers
    let numbers = extract_values(&mut data).expect("Could not parse lines.");

    // Find the first duplicate
    let dup = hunt_duplicate(&numbers);

    println!("First duplicate = {}", dup);
}

/// Reads all lines from the file with the given filename, and returns the lines
/// as a vector of strings as a Result.
///
/// # Arguments
///
/// * `filename` - The name of the file to read
///
/// # Returns
///
/// A result containing the lines of the read file as a vector of strings.
///
/// # Example
/// ```
/// let data : Vec<String> = read_lines("file.txt")?;
/// ```
fn read_lines(filename: &str) -> io::Result<Vec<String>> {
    let file = File::open(&filename)?;

    let mut reader = io::BufReader::new(file);
    let mut buf = String::new();

    let mut results : Vec<String> = Vec::new();
    while reader.read_line(&mut buf)? > 0 {
        results.push(buf.trim_right().to_string());
        buf.clear();
    }

    Ok(results)
}

/// Converts the strings in the given vector into integers, checking the
/// first character in each string for a "+" or "-", indicating positive
/// and negative numbers respectively, then parsing the remaining characters
/// as an integer.
///
/// # Arguments
///
/// * `data` - A vector of strings in the form eg. "+32"
///
/// # Returns
///
/// A result containing a vector of all parsed integer values.
///
/// # Example
/// ```
/// let numbers: Vec<i32> = extract_values(&data)?;
/// ```
fn extract_values(data: &mut Vec<String>) -> Result<Vec<i32>, String> {
    let mut results : Vec<i32> = Vec::new();

    for datum in data {
        let sign : &str = &datum[0..1];
        let s : &str = &datum[1..];

        match s.parse::<i32>() {
            Ok(number) => {
                results.push(if sign == "-" {number * -1} else {number});
            },
            Err(e) => return Err(e.to_string())
        }
    }

    Ok(results)
}

/// Sums together all values in the given vector of numbers sequentially, repeatedly, until
/// a duplicate interim sum value is found.  This value is then returned.
///
/// # Arguments
///
/// * `numbers`- A vector of integer values to sequentially sum repeatedly
///
/// # Returns
///
/// The integer value of the first duplicate sum
///
fn hunt_duplicate(numbers: &Vec<i32>) -> i32 {
    let mut sum = 0;
    let mut seen : HashSet<i32> = HashSet::new();
    seen.insert(0);

    // iterate through items indefinitely
    loop {
        for num in numbers {
            sum += *num;
            if seen.contains(&sum) { return sum; }
            seen.insert(sum);
        }
    }
}

