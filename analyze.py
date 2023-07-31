import subprocess
import os
import math
from typing import Any, Union
import plotly.express as px
import plotly.graph_objs as go
import re


class CodeQualityAnalyzer:
    """
    A helper tool to reason about code quality from looking at % of
    comments and log statments
    """

    def __init__(
        self,
        base_path: str,
        exclude_dirs: list[str],
        ext: Union[str, None] = None,
        tmp_file="tmp_all.txt",
        verbose=True,
        run_cloc=True,
    ):
        """
        Initializes and performs the analysis. Once complete, can be served
        :param str base_path: The base path (folder) to analyze
        :param list[str] exclude_dirs: Directories that will be ignored in
                analysis
        """
        # Temporary files for negotiating with cloc
        ignore_file = "tmp_ignore.txt"
        tmp_out = None
        with open(ignore_file, "w") as fout:
            for directory in exclude_dirs:
                fout.write(f"{base_path}/{directory}\n")
        if verbose:
            print("Gathering and analyzing files (1/3)")
        try:
            # Analyze all the files using `cloc` and write to file
            if run_cloc:
                tmp_out = open(tmp_file, "w")
                with subprocess.Popen(
                    [
                        "cloc",
                        base_path,
                        "--by-file",
                        "--quiet",
                        "--exclude-list-file",
                        ignore_file,
                    ],
                    stdout=tmp_out,
                ) as proc:
                    proc.communicate()
                    proc.wait()
                tmp_out.close()
            # Generate the hierachy and extract data
            if verbose:
                print("Generating hierarchy (2/3)")
            with open(tmp_file) as fin:
                lines = fin.readlines()
            lines = lines[4:-3]  # Include only the meat of report
            self.path2data = {}
            for line in lines:
                (path, blank, comment, code) = re.split(r"\s{2,}", line)
                self.path2data[path] = (int(code), int(comment), int(blank))
            self.file_hierarcy = {}
            num_source = 0
            i = len(base_path) + 1
            for file in self.path2data:
                if ext is not None and ext not in file:
                    continue
                file = file[i:]
                parts = file.split("/")
                last_data = self.file_hierarcy
                for part in parts:
                    if part not in last_data:
                        num_source += 1
                        last_data[part] = {}
                    last_data = last_data[part]
            # Construct data for treemap
            if verbose:
                print("Preparing treemap (3/3)")
            self.counts: dict[str, int] = {}
            self.ids: list[str] = []
            self.names: list[str] = []
            self.parents: list[str] = []
            self.ncode: list[int] = []
            self.ncomms: list[int] = []
            self.nblank: list[int] = []
            diff = self.recursively_analyze(self.file_hierarcy, base_path, "root")
            self.ids.append("root")
            self.names.append("root")
            self.parents.append("")
            self.ncode.append(diff[0])
            self.ncomms.append(diff[1])
            self.nblank.append(diff[2])
        finally:
            if tmp_out:
                tmp_out.close()
            os.remove(ignore_file)

    def recursively_analyze(
        self, subdata: dict[str, Any], path: str, parent_name: str
    ) -> tuple[int, int, int]:
        """
        Given a subtree of the file hierachy, analyze all files/folders within
        and write data back to `self.names`, `self.ncode`, `self.parents`,
        `self.ncomms`, and `self.nlogs` in a way that can be used to generate
        treemaps
        :param dict[str, any] subdata: The subtree being analyzed
        :param str path: Path to this subtree (so we can reconstruct filepath)
        :param str parent_name: Name of the parent node
        :param bool verbose=False: Should we tqdm this?
        :returns tuple[int, int, int]: Represents ncode, ncomms, nblank
        """
        total = (0, 0, 0)
        for key, val in subdata.items():
            self.counts[key] = self.counts.get(key, -1) + 1
            unique_key = f"{key}__{self.counts[key]}"
            if val != {}:
                diff = self.recursively_analyze(val, f"{path}/{key}", unique_key)
            else:
                full_path = f"{path}/{key}"
                diff = self.path2data[full_path]
            self.ids.append(unique_key)
            self.names.append(key)
            self.parents.append(parent_name)
            self.ncode.append(diff[0])
            self.ncomms.append(diff[1])
            self.nblank.append(diff[2])
            total = (total[0] + diff[0], total[1] + diff[1], total[2] + diff[2])
        return total

    def generate_treemap(self) -> go.Figure:
        """
        Creates and returns the treemap figure
        """
        data = [
            {
                "% Comments": comms / (code + comms + blank),
                "Lines of Code": code,
                "Comment Lines": comms,
                "Blank Lines": blank,
            }
            for code, comms, blank in zip(self.ncode, self.ncomms, self.nblank)
        ]
        fig = px.treemap(
            ids=self.ids,
            names=self.names,
            hover_name=self.names,
            values=[math.log10(thing["Lines of Code"] + 1) for thing in data],
            parents=self.parents,
            color=[thing["% Comments"] for thing in data],
            range_color=[0, 0.4],
        )
        return fig


if __name__ == "__main__":
    analyzer = CodeQualityAnalyzer(
        base_path="../nutanix-era-airavata",
        exclude_dirs=[],
        ext=".py",
        run_cloc=True,
    )
    fig = analyzer.generate_treemap()
    fig.show()
