from datetime import datetime
import pandas as pd

from raspberry_printer.config import MY_LEARNING_BOOK_RESOURCE


def make_kai_xin_learning_text(data):
    info_time = f"Time: {str(datetime.now())}\n\n"
    unit_list = data.get("unit_list")
    if not unit_list:
        # first three units
        unit_list = [1, 2, 3]
    text = "新的单元单词 str(unit_list)"
    dt = pd.read_csv(MY_LEARNING_BOOK_RESOURCE)
    dt = dt[dt["UnitID"].isin(unit_list)]
    return info_time + text + "\n".join(dt["Word"].to_list())
