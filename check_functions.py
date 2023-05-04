import sqlite3


def get_model_status(user_id):
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"SELECT status FROM model_status WHERE user_id = ?"
    cursor.execute(query, (user_id,))

    status = cursor.fetchone()
    if status:
        status_value = status[0]
    else:
        status_value = None

    cursor.close()
    conn.close()
    return status_value


def check_start(user_id):
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"SELECT start_time FROM daily_start_and_stop WHERE user_id = ?"
    cursor.execute(query, (user_id,))

    start_time = cursor.fetchone()
    if start_time:
        start_value = start_time[0]
    else:
        start_value = None

    cursor.close()
    conn.close()
    return start_value


def check_stop(user_id):
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"SELECT stop_time FROM daily_start_and_stop WHERE user_id = ?"
    cursor.execute(query, (user_id,))

    stop_time = cursor.fetchone()
    if stop_time:
        stop_value = stop_time[0]
    else:
        stop_value = None

    cursor.close()
    conn.close()
    return stop_value


def check_timed_start(user_id):
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"SELECT timed_start FROM daily_start_and_stop WHERE user_id = ?"
    cursor.execute(query, (user_id,))

    timed_start = cursor.fetchone()
    if timed_start:
        timed_start_value = timed_start[0]
    else:
        timed_start_value = None

    cursor.close()
    conn.close()
    return timed_start_value
