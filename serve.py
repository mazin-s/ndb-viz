from flask import Flask, render_template


app = Flask(
    __name__,
    static_url_path="",
    static_folder="frontend/build",
    template_folder="frontend/build",
)

typs = ["comments", "logs"]
exts = ["*", "py", "java"]

data = {}
for typ in typs:
    data[typ] = {}
    for ext in exts:
        data[typ][ext] = open(f"data/{typ}/{ext}.json").read()


@app.route("/get_graphs")
def get_graphs():
    """Gets the graph data for the frontend"""
    return data


@app.route("/")
def viz():
    """The route that renders stuff"""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
