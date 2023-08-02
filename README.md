# NDB Code Visualizer

## Overview

This tool aims to give us exploratory insight into the NDB code base. It was originally created to answer the questions:

- _What parts of the NDB codebase lack adequate comments?_
- _What parts of the NDB codebase lack adquate logging?_

In answering these questions, we ended up creating a lightning-fast code analyzer which can take arbitrary regex strings and count what percentage of lines match these strings.

### How it Works

The problem is broken down into three parts:

- Analyzing the code quickly
- Aggregating file-by-file analysis according to the folder hierarchy
- Displaying these results to the user in a ~~fun~~ informative way

**Code Analysis**

The first version of the code analyzer was built using `cloc` (a command line tool) and Python. While it worked, it was slow. The second version uses rust and `tokei`. Analysis on the entire NDB completes on a Macbook in ~2 seconds.

This code lives in `src/main.rs`. The TLDR of the code is:

1. `fn run_tokei` runs `tokei` as a subcommand excluding `*.md` and `*.txt` to analyze all files in the base directory recursively. These results are written to `out.txt`.
2. `struct Insight` represents an "insight" and is nothing more than a human-readable label and a collection of associated regexes. 
3. `fn quanitfy_insight` takes a file and an `Insight` and returns the count of the lines matching something in this `Insight`.
4. `fn add_insights_to_output` takes a path to the `tokei` output and a list of insights and extends the output of `tokei` to include user-defined insights.
5. `fn run_python` calls the code that constructs the file hierarchy.

**Hierarchy Construction**

Once all the results are in `out.txt`, a Python script (`analyze.py`) reads this file and constructs the hierarchy in a way that can be understood by Plotly (the tool that is used to make the final graph). TLDR:

1. `class CodeQualityAnalyzer` has a few lists and a nifty recursive function which constructs trees of information in the form that Plotly expects.
2. `CodeQualityAnalyzer.generate_treemap_for_ext` creates a JSON-serializable figure using Plotly (for a specific extension) and returns it.
3. When running as `__main__`, it cleans the `data` folder (where these^ figures are stored) and regenerates them on `"logs", "comments"` for `".*", ".py", ".java"`.

**Displaying to the User**

A simple flask app (`serve.py`) loads the figures from `data` into memory and stands up to serve them to the frontend app. A simple `nextjs` frontend (`frontend` directory) spins up a basic user interface which is what the user ends up hitting. When it needs to fetch/refresh the data, it talks to the local Flask app which runs the underlying commands.

## Running

Do the following:

### Setup Folders

As written, this tool assumes that the relative path from _this README_ file to the `nutanix-era-airavata` repo is `../nutanix-era-airavata` _and_ that you've configured an `ssh` key without a local password so `git pull` on `master` will work without input. This is needed for handling refreshes.

### Run Flask

```shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 serve.py
```

### Build and Serve the Frontend

```shell
cd frontend
nvm use 20
npm install
npm run build
npm run start
```

## Extensibility

NOTE: Even though this is V2, it's still a rough tool. I'm not saying that any of the below are "clean" or "good" ways of handling extensibility. Feel free to submit PRs to make this tool better. This is just where I'm leaving it for now.

### I Want to Analyze `.<something>` Files

1. Add it to the list `exts` at the bottom of `analyze.py`.
2. Add it to the list `exts` at the top of `serve.py`.
3. Add it to the list `ALL_EXTENSIONS` at the top of `frontend/app/page.tsx`.

### I Want to Add My Own Custom Regex

1. Create an `Insight` in `src/main.rs::main`. You can group multiple regexes together here. I'm assuming that you named your insight `foo`.
2. Make sure your insight is included in the `vec!` passed to `add_insights_to_output`. You can test it works by running `cargo run` and confirming that `out.txt` includes `foo` as a column.
3. Add `foo` to the list `typs` at the bottom of `analyze.py`.
4. Add `foo` to the list `typs` at the top of `serve.py`.
5. Add `foo` to the list `ALL_TYPS` at the top of `frontend/app/page.tsx`.

### I Want to Change How the Treemap Looks

A.k.a _"I don't like the colors you chose"._

1. Consult the docs [here](https://plotly.com/python-api-reference/generated/plotly.express.treemap.html).
2. Change the `generate_treemap_for_ext` function accordingly.
