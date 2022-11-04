import json
from flask import Flask, request

from raspberry_printer.printer import call_printer
from raspberry_printer.config import SECRET_TOKEN
from raspberry_printer.ci_chang import make_kai_xin_learning_text
from raspberry_printer.github import make_github_new_text


app = Flask(__name__)

TYPE_DICT = {
    "github": make_github_new_text,
    "ci_chang": make_kai_xin_learning_text,
}

SUPPORT_TYPE = list(TYPE_DICT.keys())


@app.route("/")
def index():
    return "<h1>Index Page</h1>"


@app.route("/call_bluetooth", methods=["POST"])
def call_bluetooth():
    headers = request.headers
    auth = headers.get("X-Api-Key", "")
    if auth != SECRET_TOKEN:
        return (
            json.dumps(
                {
                    "success": False,
                    "err": "You need secret token same in the cofig file",
                }
            ),
            200,
            {"ContentType": "application/json"},
        )
    data = json.loads(request.data.decode('utf8'), strict=False)
    text = ""
    if data:
        to_printer_type = data.get("type", "")
        if to_printer_type not in SUPPORT_TYPE:
            return (
                json.dumps(
                    {
                        "success": False,
                        "err": f"do not support this type {to_printer_type} for now",
                    }
                ),
                200,
                {"ContentType": "application/json"},
            )
        text = TYPE_DICT[to_printer_type](data)
    else:
        return (
            json.dumps({"success": False, "err": "no data here please check"}),
            200,
            {"ContentType": "application/json"},
        )
    if text:
        try:
            call_printer(None, text, to_printer_type=="github", github_type=data.get("info_type", ""))
            return (
                json.dumps({"success": False, "err": "no generate text to print"}),
                200,
                {"ContentType": "application/json"},
            )

        except Exception as e:
            return (
                json.dumps({"success": False, "err": str(e)}),
                503,
                {"ContentType": "application/json"},
            )
    return (
        json.dumps({"success": False, "err": "no generate text to print"}),
        200,
        {"ContentType": "application/json"},
    )


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
