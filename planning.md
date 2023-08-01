# Planning

## Version 2

### Needs...

- Ability to measure log statements
    - To solve this, I should probably just added support for arbitrary regex recognition,
- Better color scheme
- Blame
    - See arbitrary regex above
- Ability to take in arbitrary repos

### So...

Plan is to make the analysis code in rust. It will first just use out of the box tokei to do get the code, comment, blank count. This also has the nice benefit of globbing the directory with whatever excludes we end up wanting to apply.

Then, we have a struct called CodeInsight which has

- Display name (unique name)
- List of regexes to check for

While still in rust, we'll go over all the files in `out.txt` and then apply each of the CodeInsight things to get line counts, write to the `out.txt` at the end of each line.

_Then_ we'll be good to move over to python and reuse (but hopefully clean up) logic from before to generate and serve the plotly stuff.
