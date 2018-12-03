

pub mod files {
    use std::fs::File;
    use std::io;
    use std::io::prelude::*;

    pub fn read_lines(filename: &str) -> io::Result<Vec<String>> {
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

}
