import sqlite3


def update_on_off(user_id):
    """
    Updates the status of the monitoring to on
    :param user_id:
    :return:
    """
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"UPDATE model_status SET status = ? WHERE user_id = ?"
    cursor.execute(query, (1, user_id))

    conn.commit()
    cursor.close()
    conn.close()


def update_off_on(user_id):
    """
    Updates the status of the monitoring to off
    :param user_id:
    :return:
    """
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"UPDATE model_status SET status = ? WHERE user_id = ?"
    cursor.execute(query, (0, user_id))

    conn.commit()
    cursor.close()
    conn.close()


def update_timed_start(user_id, chosen_state: bool):
    """
    Updates the status of the monitoring to on
    :param user_id: Database user id
    :param chosen_state: The state of the monitoring setting type
    :return:
    """
    db_path = r"C:\Users\stapi\PycharmProjects\home\instance\home_owner.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = f"UPDATE daily_start_and_stop SET timed_start = ? WHERE user_id = ?"
    cursor.execute(query, (chosen_state, user_id))

    conn.commit()
    cursor.close()
    conn.close()
