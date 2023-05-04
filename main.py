from typing import Generator, Optional, Any, Tuple
import requests
import torch
import cv2
import numpy as np
from datetime import datetime
import time
import os
import queue
from PIL import Image
from notification_manager import Notify
# from email_notification import EmailNotify
from multiprocessing import Process
from numba import jit
import gc
from check_functions import get_model_status, check_start, check_stop, check_timed_start
from update_functions import update_on_off, update_off_on, update_timed_start


now = datetime.now()
objects_queue = queue.Queue()
ADMIN_NUMBER = os.environ.get("MY_NUMBER_TWO")
CLIENT_NUMBER = os.environ.get("CLIENT_NUMBER_TWO")
notification = Notify(sid=os.environ.get("Account_SID"),
                      auth=os.environ.get("AUTH_TOKEN"),
                      admin_number=ADMIN_NUMBER,
                      client_number=CLIENT_NUMBER)

# For handling email notifications
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_EMAIL_APP_PASSWORD = os.environ.get("ADMIN_EMAIL_APP_PASSWORD")
DESTINATION_EMAIL = os.environ.get("DESTINATION_EMAIL")
IMAGE_PATH = 'runs/detect/exp/image0.jpg'
# email_notify = EmailNotify(admin_email_address=ADMIN_EMAIL,
#                            admin_email_password=ADMIN_EMAIL_APP_PASSWORD,
#                            to_email_address=DESTINATION_EMAIL,
#                            img_path=IMAGE_PATH)

USERNAME = os.environ.get('APP_USERNAME')
PASSWORD = os.environ.get('APP_PASSWORD')


# directory_path = "C:/Program Files/ngrok-v3-stable-windows-amd64/"
# subprocess.run(["ngrok", "http", "5000"], cwd=directory_path)
# user = User(email="mkhulu", password="elgefefe")


def clean_up_cam(path: str) -> None:
    path_cam_two = path
    extension = '.jpg'
    for file_name in os.listdir(path_cam_two):
        if file_name.endswith(extension):
            os.remove(os.path.join(path_cam_two, file_name))
    print(f"{path} is clean.")


def image_handler(path: str) -> Generator[str, None, None]:
    cam_image_dir = path
    cam_image_files = [f for f in os.listdir(cam_image_dir) if os.path.isfile(os.path.join(cam_image_dir, f))]
    return (os.path.join(cam_image_dir, image_file) for image_file in cam_image_files)


@jit(nopython=True)
def cropped_image(img: np.ndarray,
                  x_one_left_to_right: int,
                  y_one_top_to_bottom: int,
                  x_two_right_to_left: int,
                  y_two_bottom_to_top: int) -> np.ndarray:
    height, width = img.shape
    # print(f"image height: {height}, image width {width}.")
    # Set the coordinates of the top-left and bottom-right corners of the cropping rectangle
    x1, y1 = x_one_left_to_right, y_one_top_to_bottom  # top-left corner
    x2, y2 = x_two_right_to_left, y_two_bottom_to_top  # bottom-right corner

    # Crop the image using NumPy slicing
    cropped_img = img[y1:y2, x1:x2]
    return cropped_img


@jit(nopython=True)
def compare_images_numba(current_image: np.ndarray, base_image: np.ndarray) -> Tuple[float, bool]:
    if np.array_equal(base_image, current_image):
        print("arrays are the same.")
        return 0.0, False
    else:
        diff = np.abs(base_image.astype(np.float32) - current_image.astype(np.float32))
        score = np.sum(diff) / (diff.shape[0] * diff.shape[1])
        return score, True


def compare_images(current_image: np.ndarray, base_image_path: str) -> Tuple[float, bool]:
    base_image = np.array(cv2.imread(f"{base_image_path}/base_image.jpg", cv2.IMREAD_GRAYSCALE))
    return compare_images_numba(current_image, base_image)


def cam_gen_frames(cam_name: str, cam_url: str, path: str, base_image_path: str, base_conf_level: float = 0.50,
                   x1: Optional[int] = 0, y1: Optional[int] = 0, x2: Optional[int] = 0, y2: Optional[int] = 0) -> None:
    camera_name = f"{cam_name}"
    print(f"{camera_name} run is starting...")
    model2: Any = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    url: str = str(cam_url)
    count = 5
    picture = 1
    detected = 1
    run = True
    state_check_interval = 60  # setting iteration duration.
    start_time = time.time()
    new_width, new_height = 640, 480
    # base_img = np.array(cv2.imread(f"{base_image_path}/base_image.jpg", cv2.IMREAD_GRAYSCALE))
    while run:
        time.sleep(0.2)
        kill_process = get_model_status(1)  # to kill the process if the user switches it off on their webpage.
        if not kill_process:
            print(f"Shutting down for {camera_name}...")
            model2 = None
            gc.collect()
            run = False
        elapsed_time = time.time() - start_time

        if check_timed_start(1) and datetime.now().strftime("%H:%M") == check_stop(user_id=1)[:5]:
            update_off_on(1)
            update_timed_start(1, False)
            print("update to off")

        if elapsed_time >= state_check_interval:
            picture = 1
            start_time = time.time()
            print("Base image refreshing")
        try:
            resp = requests.get(url, stream=True).raw
            img: np.array = np.asarray(bytearray(resp.read()), dtype="uint8")
            img: np.array = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
            # We are setting a base image that will be used for comparison to avoid checking images that are not
            # different from a cleared base image.
            height, width = img.shape
            img = cropped_image(img,
                                x_one_left_to_right=x1,
                                y_one_top_to_bottom=y1,
                                x_two_right_to_left=width - x2,
                                y_two_bottom_to_top=height - y2)
            img = cv2.resize(img, (new_width, new_height))

            if run and picture > 0:
                base_img_results = model2([img])
                for detection in base_img_results.xyxy[0]:  # Checking that base image does not have a person in it.
                    # Ruling out low probability of it being a person.
                    if detection[5] != 0:
                        picture = 0
                        base_image = Image.fromarray(img)
                        base_image.save(f"{base_image_path}/base_image.jpg")
                        base_image = None
                        gc.collect()
                    elif detection[5] == 0 and detection[4] > (base_conf_level - 0.30):
                        # cam_two_image.save(f"{path}/{count}image.jpg")
                        # notification.make_a_call()
                        # notification.notify_me(f"A person has been detected on {camera_name} at {time.ctime()} "
                        #                        f"check your camera to verify. You can review the pictures "
                        #                        f"on your webapp.")
                        print(f"Person found on {camera_name}, Please check it out"
                              f" before turning the monitoring on again")
                        print("SMS Notification sent.")
                        # email_notify.send_message(time.ctime())
                        # print("Email notification sent.")
                        time.sleep(10)
                        run = False

            if run and picture == 0:
                score, is_different = compare_images(img, base_image_path)
                if run and is_different and score > 10:
                    print("The arrays have a difference score of:", score)
                    gc.collect()
                    cam_results = model2([img])
                    for detection in cam_results.xyxy[0]:
                        if detection[5] == 0 and detection[4] > base_conf_level:
                            print(f"{count}{detection[4]} {detection[5]} {time.ctime().replace(' ', '-')}")
                            if detected == 1:
                                cam_results.show()
                                # cam_two_image.save(f"{path}/{count}image.jpg")
                                # notification.make_a_call()
                                # notification.notify_me(f"A person has been detected on {camera_name} at {time.ctime()} "
                                #                        f"check your camera to verify. You can review the pictures "
                                #                        f"on your webapp.")
                                print(f"Person found on {camera_name}, score: {score}")
                                print("SMS Notification sent.")
                                # email_notify.send_message(time.ctime())
                                # print("Email notification sent.")
                                detected = 0

                            if run and count > 0:
                                cam_two_image = Image.fromarray(cam_results.ims[0])
                                cam_two_image.save(f"{path}/{count}-image.jpg")
                            elif run and count == 0:
                                print("Taking a 5 second nap.")
                                time.sleep(5)
                                count = 5
                                picture = 1
                                detected = 1
                            count -= 1
                        else:
                            continue
            img = None
            gc.collect()

        except requests.exceptions.ConnectionError:
            print(f"The camera is not connecting. Check your url: {url}")
            run = False
            return


user_id = 1

on = bool(get_model_status(user_id))


def kill_switch():
    kill_process = get_model_status(1)
    if kill_process:
        return True


def handle_cameras():
    global on
    global progress

    while progress:

        p1 = Process(target=cam_gen_frames,
                     args=("Camera One",
                           "http://192.168.3.25:8080/shot.jpg",
                           "C:/Users/stapi/PycharmProjects/home_controler/static/cam_one",
                           "static/cam_one_base_image", 0.50, 0, 0, 0, 0))
        p2 = Process(target=cam_gen_frames,
                     args=("Camera Two",
                           "http://192.168.3.25:8080/shot.jpg",
                           "C:/Users/stapi/PycharmProjects/home_controler/static/cam_two",
                           "static/cam_two_base_image", 0.30, 0, 0, 580, 0))

        p1.start()
        p2.start()
        on = bool(get_model_status(1))

        if not on:
            p1.terminate()
            p2.terminate()
            p1.join()
            p2.join()
            p1.close()
            p2.close()
            progress = False
        else:
            p1.join()
            p2.join()
            time.sleep(1)


if __name__ == '__main__':
    user_id = 1
    on = bool(get_model_status(user_id))
    progress = None

    while True:
        on = bool(get_model_status(user_id))

        if progress:
            pass
        else:
            while not on:
                on = bool(get_model_status(user_id))
                if check_start(user_id=user_id) and (
                        datetime.now().strftime("%H:%M") == check_start(user_id=user_id)[:5]):
                    update_on_off(user_id=user_id)
                    update_timed_start(user_id=user_id, chosen_state=True)
                    print("updated")
                time.sleep(5)
            else:
                print(on)
                progress = True
                handle_cameras()
