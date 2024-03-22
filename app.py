import json
import pickle
from flask import Flask, request
from flask_apscheduler import APScheduler
from datetime import datetime
import os

from raspberry_printer.printer import call_printer
from raspberry_printer.config import SECRET_TOKEN
from raspberry_printer.ci_chang import make_kai_xin_learning_text
from raspberry_printer.github import make_github_new_text

from openai import OpenAI
from pycoingecko import CoinGeckoAPI


cg = CoinGeckoAPI()


app = Flask(__name__)
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

TYPE_DICT = {
    "github": make_github_new_text,
    "ci_chang": make_kai_xin_learning_text,
}

SUPPORT_TYPE = list(TYPE_DICT.keys())

# global variable to store the coins when restart the server the coins will be reset
COINS_PRINCE_LIST = []


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
    data = json.loads(request.data.decode("utf8"), strict=False)
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
            call_printer(
                None,
                text,
                to_printer_type == "github",
                github_type=data.get("info_type", ""),
            )
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


@scheduler.task("interval", id="job_2", minutes=30)
def bitcoins_show():
    # try to make client, the client will lose connection after a while so we make it every time
    client = None
    try:
        client = OpenAI()
        if os.environ.get("OPENAI_API_BASE"):
            client = OpenAI(base_url=os.environ.get("OPENAI_API_BASE"))
        else:
            client = OpenAI()
    except:
        pass
    text = ""
    last_bitcoin_price = None
    last_ethereum_price = None
    coins_price_list = []
    if os.path.exists("temp.bin"):
        with open("temp.bin", "rb") as f:
            coins_price_list = pickle.load(f)
    print(coins_price_list)

    if coins_price_list:
        last_bitcoin_price = coins_price_list[-1].get("bitcoin", None).get("usd", None)
        last_ethereum_price = (
            coins_price_list[-1].get("ethereum", None).get("usd", None)
        )
    coins_price_now_dict = cg.get_price(
        ids=["ethereum", "bitcoin"], vs_currencies=["usd", "cny"]
    )
    coins_price_list.append(coins_price_now_dict)
    with open("temp.bin", "wb") as f:
        pickle.dump(coins_price_list, f)
    now_bitcoin_price = coins_price_now_dict.get("bitcoin", {}).get("usd", None)
    now_ethereum_price = coins_price_now_dict.get("ethereum", {}).get("usd", None)
    now = str(datetime.now())
    text = f"Now is: {now}\n"
    if (
        last_bitcoin_price
        and last_ethereum_price
        and now_bitcoin_price
        and now_ethereum_price
    ):
        text += f"Bitcoin: {last_bitcoin_price} -> {now_bitcoin_price}\n"
        text += f"Ethereum: {last_ethereum_price} -> {now_ethereum_price}\n"
    else:
        text += f"----> Bitcoin: {now_bitcoin_price}\n"
        text += f"----> Ethereum: {now_ethereum_price}\n"
    text += "\n"
    if client:
        if (
            last_bitcoin_price
            and now_bitcoin_price > last_bitcoin_price
            and (now_bitcoin_price - last_bitcoin_price) / last_bitcoin_price > 0.001
        ):
            prompt = f"比特币涨了 {now_bitcoin_price-last_bitcoin_price} USD 请写一段说明我厉害的话，answer in Chinese or English Choose one to answer"
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model="gpt-4-0613"
            )
            answer = completion.choices[0].message.content.encode("utf8").decode()
            text += "夸我一下：\n"
            text += answer
        if (
            last_bitcoin_price
            and now_bitcoin_price < last_bitcoin_price
            and (last_bitcoin_price - now_bitcoin_price) / last_bitcoin_price > 0.001
        ):
            prompt = f"比特币跌了 {last_bitcoin_price-now_bitcoin_price} USD 请写一段激励我给我信心的话，answer in Chinese or English Choose one to answer"
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model="gpt-4-0613"
            )
            answer = completion.choices[0].message.content.encode("utf8").decode()
            text += "激励我一下：\n"
            text += answer

    call_printer(None, text)


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
