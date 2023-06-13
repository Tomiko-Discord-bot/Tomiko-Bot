from datetime import datetime as dt


def get_time() -> str:
    return dt.now().strftime('%H:%M:%S')
