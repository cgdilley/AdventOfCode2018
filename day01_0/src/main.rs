use std::fs::File;
use std::io;
use std::io::prelude::*;

fn main() {
    // Read the lines from the file
    let mut data = read_lines("../input/day1.txt").expect("Could not load file.");

    // Convert the lines into integers
    let numbers = extract_values(&mut data).expect("Could not parse lines.");

    // Calculate the sum
    let sum = sum_vector(& numbers);

    println!("The sum = {}", sum);
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
/// `
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
/// `
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

/// Calculates the sum of all values in the given vector of integers
///
/// # Arguments
///
/// * `numbers` - A vector of integer values to sum
///
/// # Returns
///
/// The sum of the integer values in the given vector
///
fn sum_vector(numbers: &Vec<i32>) -> i32 {
    let mut sum = 0;
    for num in numbers {
        sum += *num;
    }
    sum
}

