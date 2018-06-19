# coding:utf-8

import os
import pickle
import requests


def download_image(url, timeout = 15):
    try:
        response = requests.get(url, allow_redirects=False, timeout=timeout)
        if response.status_code != 200:
            e = Exception("HTTP status: " + response.status_code)
            raise e
        content_type = response.headers["content-type"]
        if 'image' not in content_type:
            e = Exception("Content-Type: " + content_type)
            raise e
        return response.content
    except Exception as ex:
        print(str(ex))
        return None

def save_image(filename, image):
    with open(filename, "wb") as f:
        f.write(image)

def save_pickle(target, filename, blog_data_dir):
    if not os.path.exists(blog_data_dir):
        os.makedirs(blog_data_dir)
    with open("{}/{}.p".format(blog_data_dir, filename), "wb") as f:
        pickle.dump(target, f)
