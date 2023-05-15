import os
import tweepy
import json
import time
from pprint import pprint
from discordwebhook import Discord
from keep_arive import keep_alive

# API情報
api_key = os.environ["TWITTER_API_KEY"]
api_key_secret = os.environ["TWITTER_API_KEY_SECRET"]
bearer_token = os.environ["TWITTER_BEARER_TOKEN"]

# discordのWebhook URL
discord = Discord(url=os.environ["DISCORD_WEBHOOK_URL"])

with open("data.txt", "r") as f:
    lines = f.readlines()
    urls = []
    for line in lines:
        urls.append(line.strip())


class StreamListener(tweepy.StreamingClient):
    def on_data(self, raw_data: str):
        ljson = json.loads(raw_data)
        pprint(ljson)
        try:
            init = ljson["data"]["text"][0]
        except KeyError as e:
            print(e)
            return
        if init == "@":
            try:
                url = (
                    "https://twitter.com/"
                    + ljson["includes"]["users"][1]["username"]
                    + "/status/"
                    + ljson["data"]["referenced_tweets"][-1]["id"]
                )
                if url in urls:
                    pass
                else:
                    discord.post(content=url)
                    urls.append(url)
            except IndexError as e:
                print(e)
            except KeyError as e:
                print(e)
        else:
            url = (
                "https://twitter.com/"
                + ljson["includes"]["users"][0]["username"]
                + "/status/"
                + ljson["data"]["edit_history_tweet_ids"][0]
            )
            if url in urls:
                pass
            else:
                discord.post(content=url)
                urls.append(url)
        with open("data.txt", "w") as f:
            f.write("\n".join(urls))
        time.sleep(30)  # 接続は50回/15分
        return

    def on_request_error(self, status_code):
        print("リクエストエラー：" + str(status_code))
        if status_code == 429:
            time.sleep(1020)
        return


stream = StreamListener(bearer_token, wait_on_rate_limit=True)
stream.add_rules(
    tweepy.StreamRule(
        value="(#SfC本選 OR #StageforCinderella) 募集 (ダイマ OR (投票 OR 投票先) OR リプ) -is:retweet"
    )
)
stream.add_rules(
    tweepy.StreamRule(
        value="(((検索 OR FF外) 失礼) OR はじめまして OR 初めまして) (お願いします OR お願い致します OR お願いいたします OR お力添え) (アイドル OR ダイマ) -交換 -お譲り -フォロー -仲良く -ありがとう is:reply -is:retweet"
    )
)

# deleting = stream.delete_rules(ids=1656950266502184960)

rules = stream.get_rules()
print(rules)

keep_alive()

stream.filter(
    expansions=[
        "author_id",
        "edit_history_tweet_ids",
    ],
    tweet_fields=[
        "referenced_tweets",
    ],
    user_fields=[
        "name",
        "username",
    ],
)
