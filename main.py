import config
import tweepy
import subprocess
import sys
from tqdm.contrib.concurrent import process_map
import schedule
import time

log = open(config.LOG_DIR, 'w+')


def get_list_members(list_id):
    data = []
    res = None
    while res is None or "next_token" in res.meta:
        res = client.get_list_members(
            list_id, user_auth=True, 
            pagination_token=None if res is None else res.meta["next_token"])
        data += res.data
    return data


def get_lists(id):
    return client.get_owned_lists(id, user_auth=True).data


def get_list_name(l):
    return f"{l['name']}-{l['id']}"


def exec_gallery(item):
    list_name = item["listName"]
    name = item["username"]
    id = item["id"]
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
    seq = []
    for l in all_lists:
        name = get_list_name(l)
        print(f"Now getting list: {name}")
        l2 = [ { "id": i["id"], "username": i["username"], "listName": name } 
               for i in get_list_members(l["id"]) ]
        seq += l2
    print(f"total need renew: {len(seq)}")
    process_map(exec_gallery, seq, max_workers=int(config.MAX_WORKERS))


# first run may cause massive downloading, take more than 2 hours
update()

schedule.every(2).hours.do(update)

while True:
    schedule.run_pending()
    time.sleep(1800)
