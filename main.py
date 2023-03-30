import config
import tweepy
import subprocess
import sys
from tqdm import tqdm
import schedule
import time

log = open('gallery.log', 'w')


def get_list_members(list_id):
    data = client.get_list_members(list_id, user_auth=True).data
    return data


def get_lists(id):
    return client.get_owned_lists(id, user_auth=True).data


def exec_gallery(list_name, user):
    name = user["username"]
    id = user["id"]
    path = f"{config.OUTPUT_DIR}/{list_name}/{id}"
    p = subprocess.Popen(
        f"gallery-dl -u '{config.MY_USER_NAME}' -p \
            '{config.MY_PASSWORD}' 'https://twitter.com/{name}/media'\
             -v -D {path} --write-metadata",
        stdout=log, stderr=log, shell=True)
    p.wait()
    if p.returncode == 15:
        sys.exit(1)


client = tweepy.Client(
    consumer_key=config.API_KEY,
    consumer_secret=config.API_KEY_SECRET,
    access_token=config.ACCESS_KEY,
    access_token_secret=config.ACCESS_KEY_SECRET
)

user_id = config.MY_ID


def update():
    all_lists = get_lists(config.MY_ID)
    for l in all_lists:
        l2 = get_list_members(l["id"])
        print(f"Now updating: {l['name']}")
        for i in tqdm(l2, total=len(l2)):
            exec_gallery(l["name"], i)


schedule.every(2).hours.do(update)

update()

while True:
    schedule.run_pending()
    time.sleep(1800)
