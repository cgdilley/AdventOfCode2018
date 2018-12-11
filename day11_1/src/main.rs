use std::collections::HashMap;
use std::collections::hash_map::Entry::{Occupied,Vacant};

fn main() {
    let serial_number = 5535;
    let size = 300;

    let mut power = fill_grid(&serial_number, &size);

    let biggest = test_all_region_sizes(&mut power, &size);

    println!("The region with the highest power is: {:?}", biggest);
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

#[derive(Debug)]
#[derive(Copy, Clone)]
struct GridRegion {
    topleft: (i32, i32),
    power: i32,
    size: i32,
}
impl GridRegion {
    fn set(&mut self, power: i32, size: i32) {
        self.power = power;
        self.size = size;
    }
}


fn test_all_region_sizes(powers: &mut HashMap<(i32, i32), i32>, grid_size: &i32) -> GridRegion {
    let mut biggest = GridRegion {
        topleft: (0, 0),
        power: 0,
        size: 0,
    };

    let mut cache = HashMap::new();

    for size in 1..(*grid_size + 1) {
        let result = find_biggest_region(powers, *grid_size, size,
                                         &mut cache);
        if result.power > biggest.power {
            biggest = result;
        }
        println!("Tested size {}.", size);
    }

    biggest
}

fn find_biggest_region(powers: &mut HashMap<(i32, i32), i32>, grid_size: i32, region_size: i32,
                       cache: &mut HashMap<(i32, i32), GridRegion>) -> GridRegion {
    let mut biggest_coord = (0, 0);
    let mut biggest_val = 0;

    for topleft_x in 1..(grid_size - region_size + 2) {
        for topleft_y in 1..(grid_size - region_size + 2) {
            let mut entry = cache.entry((topleft_x, topleft_y));
            let mut val = 0;

            /// UGGGH this looks terrible.  Maps in Rust suck.  A lot.
            match entry {
                Vacant(e) => {
                    for x in topleft_x..(topleft_x + region_size) {
                        for y in topleft_y..(topleft_y + region_size) {
                            val += &powers[&(x, y)];
                        }
                    }
                    e.insert(GridRegion {
                        topleft: (topleft_x, topleft_y),
                        size: region_size,
                        power: val
                    });
                },
                Occupied(mut cache_result) => {
                    let cached_region : &mut GridRegion = cache_result.get_mut();

                    if cached_region.size < region_size {
                        val = cached_region.power;
                        // This cached value covers most of the square.  Need to also calc the regions
                        // to the right and below the cached region

                        // right
                        for x in (topleft_x + cached_region.size)..(topleft_x + region_size) {
                            for y in topleft_y..(topleft_y + cached_region.size) {
                                val += &powers[&(x, y)];
                            }
                        }
                        // bottom
                        for x in topleft_x..(topleft_x + region_size) {
                            for y in (topleft_y + cached_region.size)..(topleft_y + region_size) {
                                val += &powers[&(x, y)];
                            }
                        }
                    }
                    else {
                        for x in topleft_x..(topleft_x + region_size) {
                            for y in topleft_y..(topleft_y + region_size) {
                                val += &powers[&(x, y)];
                            }
                        }
                    }

                    cached_region.set(val, region_size);

                }
            }


            if val > biggest_val {
                biggest_val = val;
                biggest_coord = (topleft_x, topleft_y);
            }
        }
    }

    GridRegion {
        topleft: biggest_coord,
        power: biggest_val,
        size: region_size,
    }
}


fn get_digit(value: &i32, power: i32) -> i32 {
    return (*value / power) % 10;
}