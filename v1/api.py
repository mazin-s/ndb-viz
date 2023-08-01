import json
from flask import Flask, render_template
from analyze import CodeQualityAnalyzer
from plotly.utils import PlotlyJSONEncoder


app = Flask(__name__)


@app.route("/")
def viz_all():
    """The route that renders analysis on _all_ files"""
    analyzer = CodeQualityAnalyzer(
        base_path="../..", exclude_dirs=["utils/viz/"], run_cloc=False
    )
    plot = json.dumps(analyzer.generate_treemap(), cls=PlotlyJSONEncoder)
    return render_template("index.html", plot=plot)


@app.route("/python")
def viz_python():
    """The route that renders analysis on just python files"""
    analyzer = CodeQualityAnalyzer(
        base_path="../..", exclude_dirs=["utils/viz/"], run_cloc=False, ext=".py"
    )
    plot = json.dumps(analyzer.generate_treemap(), cls=PlotlyJSONEncoder)
    return render_template("index.html", plot=plot)


@app.route("/java")
def viz_java():
    """The route that renders analysis on just python files"""
    analyzer = CodeQualityAnalyzer(
        base_path="../..", exclude_dirs=["utils/viz/"], run_cloc=False, ext=".java"
    )
    plot = json.dumps(analyzer.generate_treemap(), cls=PlotlyJSONEncoder)
    return render_template("index.html", plot=plot)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
