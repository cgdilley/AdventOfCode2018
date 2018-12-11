use std::collections::HashMap;

fn main() {
    let serial_number = 5535;
    let size = 300;

    let mut power = fill_grid(&serial_number, &size);

    let biggest = find_biggest_region(&mut power, size, 3);

    println!("The top-left coord of the 3x3 region with the highest power is: {:?}", biggest);

}

fn fill_grid(serial_number: &i32, size: &i32) -> HashMap<(i32, i32), i32> {

    let mut map = HashMap::new();

    for x in 1..(*size + 1) {

        let rack = x + 10;

        for y in 1..(*size + 1) {

            let mut power = rack * y;
            power += serial_number;
            power *= rack;
            power = get_digit(&power, 100);
            power -= 5;

            map.insert((x, y), power);

        }
    }

    map
}

fn find_biggest_region(powers: &mut HashMap<(i32, i32), i32>, grid_size: i32, region_size: i32) -> (i32, i32) {

    let mut biggest_coord = (0, 0);
    let mut biggest_val = 0;

    for topleft_x in 1..(grid_size-region_size + 2) {
        for topleft_y in 1..(grid_size-region_size + 2) {

            let mut val = 0;

            for x in topleft_x..(topleft_x + region_size) {
                for y in topleft_y..(topleft_y + region_size) {

                    val += &powers[&(x, y)];

                }
            }

            if val > biggest_val {
                biggest_val = val;
                biggest_coord = (topleft_x, topleft_y);
            }

        }
    }

    biggest_coord
}


fn get_digit(value: &i32, power: i32) -> i32 {

    return (*value / power) % 10;

}