from flask import Flask, render_template, make_response
from flask_cors import CORS
import os


app = Flask(
    __name__,
    static_url_path="",
    static_folder="frontend/build",
    template_folder="frontend/build",
)
CORS(app)

typs = ["comments", "logs"]
exts = ["*", "py", "java"]


def refresh_data_in_memory():
    """Updates the in-memory variable `data`"""
    for typ in typs:
        data[typ] = {}
        for ext in exts:
            data[typ][ext] = open(f"data/{typ}/{ext}.json").read()


data = {}
refresh_data_in_memory()


@app.route("/get_graphs")
def get_graphs():
    """Gets the graph data for the frontend"""
    return data


@app.route("/refresh", methods=["POST"])
def refresh():
    """Crude way of refreshing the data"""
    # Go into repo master and pull
    os.system("cd ../nutanix-era-airavata && git checkout master && git pull")
    # Rerun the datagen script
    os.system("cargo run")
    # Refresh the value in memory
    refresh_data_in_memory()
    return make_response("Okay", 200)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3001, debug=True)
