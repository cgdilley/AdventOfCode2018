use std::io;

fn main() {
    loop {
        match ask_and_answer() {
            Ok(cont) => {if !cont {break}},
            Err(e) => println!("Got an error while asking question: {}", e)
        }
    }
}

fn ask_and_answer() -> Result<bool, String> {
    println!("Input a year (or quit): ");

    let mut input = String::new();
    match io::stdin().read_line(&mut input) {
        Ok(_) => {},
        Err(e) => return Err(e.to_string()),
    }

    if input.trim() == "quit" { return Ok(false)}

    match input.trim().parse::<i32>(){
        Ok(year) => {println!("{}", if is_leap(&year) {"Is a leap year"} else {"Is not a leap year"})},
        Err(e) => return Err(e.to_string())
    }

    Ok(true)
}

fn is_leap(year: &i32) -> bool {
    if year % 400 == 0 {true}
    else if year % 100 == 0 {false}
    else if year % 4 == 0 {true}
    else {false}
}

