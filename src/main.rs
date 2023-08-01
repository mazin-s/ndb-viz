use kdam::tqdm;
use regex::Regex;
use std::fs;
use std::path::Path;
use std::process::{Command, Stdio};

/// Runs tokei (via command line) to generate basic results
fn run_tokei(analyze_path: &str, output_path: &str) {
    println!("Running tokei...");
    let output = Command::new("tokei")
        .arg(analyze_path)
        .arg("--files")
        .arg("-c")
        .arg("1000")
        .arg("-e")
        .arg("*.md")
        .arg("-e")
        .arg("*.txt")
        .output()
        .expect("Failed to execute command");
    fs::write(output_path, output.stdout).expect("Can't write tokio output to file");
}

/// A flexible "insight" into the code. Nothing more than a readable name
/// and a collection of regexes that we want to count the occurence of
struct Insight {
    pub display_name: String,
    pub regexes: Vec<Regex>,
}
impl Insight {
    pub fn new(display_name: &str, regex_strs: Vec<&str>) -> Insight {
        let mut regexes: Vec<Regex> = Vec::new();
        for reg_str in regex_strs {
            let re = Regex::new(&reg_str).unwrap();
            regexes.push(re);
        }
        Insight {
            display_name: display_name.into(),
            regexes,
        }
    }
}

/// For a given file and Insight (think: collection of regexes) count how
/// many lines satisfy at least one of the regexes
fn quantify_insight(file: &str, insight: &Insight) -> i32 {
    let data = fs::read_to_string(file);
    if data.is_err() {
        return 0;
    }
    let data = data.unwrap();
    let lines = data.split("\n");
    let mut result = 0;
    for line in lines {
        for re in insight.regexes.iter() {
            if re.is_match(line) {
                result += 1;
                break;
            }
        }
    }
    result
}

/// Takes in an output file containing lines/code/comments/blank (by file) from
/// tokei and extend it with analysis in new columns using the data in insights
fn add_insights_to_output(output_file: &str, base_path: &str, insights: Vec<Insight>) {
    println!("Gaining insight...");
    let old_lines = fs::read_to_string(output_file);
    if old_lines.is_err() {
        return;
    }
    let old_lines = old_lines.unwrap();
    let old_lines = old_lines.split("\n");
    let mut new_lines: Vec<String> = Vec::new();
    let line_splitter = Regex::new(r"\s{2,}").expect("Can't make splitter");
    for (ix, line) in tqdm!(
        old_lines.clone().enumerate(),
        total = old_lines.clone().count(),
        animation = "ascii"
    ) {
        // Write the display name at the top
        let mut new_line = line.to_string();
        if ix == 1 {
            for insight in insights.iter() {
                new_line += &format!("{:>13}", insight.display_name);
            }
        } else if line.starts_with(&(" ".to_string() + base_path)) {
            for insight in insights.iter() {
                let mut parts = line_splitter.split(line);
                let filename = parts
                    .next()
                    .expect("Weird line")
                    .strip_prefix(" ")
                    .expect("Weirder line");
                let q = quantify_insight(filename, insight);
                new_line += &format!("{:>13}", q);
            }
        } else {
            if line.contains("==========") {
                new_line += "=============";
            }
            if line.contains("----------") {
                new_line += "-------------";
            }
        }
        new_lines.push(new_line);
    }
    let new_file_contents = new_lines.join("\n");
    let path = Path::new(output_file);
    fs::write(path, new_file_contents).expect("Couldn't write to file");
}

/// Generates and shows a test treemap
fn run_python(output_file: &str, base_path: &str) {
    Command::new("python3")
        .arg("analyze.py")
        .arg(output_file)
        .arg(base_path)
        .stdout(Stdio::inherit())
        .output()
        .expect("Couldn't generate with Python");
}

fn main() {
    let base_path = "../nutanix-era-airavata";
    let out_file = "out.txt";
    // Speedy base analysis by tokei
    run_tokei(base_path, out_file);
    let insight = Insight::new(
        "Logs",
        vec![
            r".*logger\.[A-Z]+.*", // Python
            r".*LOGGER\.[a-z]+.*", // Java
        ],
    );
    // Speedy custom insights
    add_insights_to_output(out_file, base_path, vec![insight]);
    // Show!
    run_python(out_file, base_path);
}
