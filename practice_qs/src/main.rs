extern crate rand;

use rand::Rng;
use std::f64;

fn main() {

    let mut list: [i32; 10000] = [0; 10000];
    fill_list(&mut list);
    shuffle(&mut list);
    print_list(&list);

    qs(&mut list);
    print_list(&list);
}

fn shuffle<T>(list: &mut [T])
{
    let mut rng = rand::thread_rng();

    for i in (1..list.len()).rev() {
        let swap_pos = rng.gen_range(0, i);
        list.swap(swap_pos, i);
    }
}

fn fill_list(list: &mut [i32])
{
    for i in 0..list.len() {
        list[i] = i as i32;
    }
}

fn print_list(list: &[i32])
{
    let fsize = (list.len() - 1) as f64;
    let num_width : u32 = (fsize.log10() as u32) + 3;
    let per_row : u32 = 40;

    let mut row = String::new();
    for (i, val) in list.iter().enumerate() {
        let mut num = val.to_string();
        while (num.len() as u32) < num_width { num = " ".to_string() + &num}
        row += &num;

        if ((i as u32) + 1) % per_row == 0 {
            println!("{}", row);
            row = String::new();
        }
    }

    let mut divider = String::new();
    while (divider.len() as u32) < 1 + (per_row * num_width) { divider += "-"}
    println!("{}", divider);
}

fn qs(list: &mut [i32])
{
    let len = list.len();
    _qs(list, 0, len)
}

fn _qs(list: &mut [i32], start: usize, end: usize)
{
    let mut left = start;
    let mut right = end - 1;
    let mut dir = false;

    while left < right
        {
            if list[left] > list[right] {
                list.swap(left, right);
                dir = !dir;
            }
            if dir {right -= 1} else {left += 1}
        }

    if left > start { _qs(list, start, left)}
    if right < end - 1 { _qs(list, right, end)}
}