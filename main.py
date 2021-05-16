import firebase_admin
import googleapiclient
from firebase_admin import credentials
from firebase_admin import db
import time
import urllib
from urllib import request
import xml.etree.ElementTree as ET
from datetime import timezone, datetime
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
import os
from os.path import join, dirname
from dotenv import load_dotenv


def main():
    # 処理前の時刻
    t1 = time.time()

    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_KEY")

    if not firebase_admin._apps:
        print('初期化')
        cred = credentials.Certificate('hologram-firebase-adminsdk.json')

        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
        })

    ref_db = db.reference('/video')

    YOUTUBE_API_KEY = YOUTUBE_API_KEY
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # チャンネルIDリスト

    channelIdList = [
        'UCp6993wxpyDPHUpavwDFqgg',
        'UC0TXe_LYZ4scaW2XMyi5_kw',
        'UCDqI2jOz0weumE8s7paEk6g',
        'UC-hM6YJuNYVAmUWxeIr9FeA',
        'UCdn5BQ06XqgXoAxIhbqw5Rg',
        'UCQ0UDLQCjY0rmuxCDE38FGg',
        'UCD8HOxPs4Xvsm8H0ZxXGiBw',
        'UC1CfXB_kRs3C-zaeTG3oGyg',
        'UCFTLzh12_nrtzqBPsTCqenA',
        'UC1opHUrw8rvnsadT-iGp7Cg',
        'UCp3tgHXw_HI0QMk1K8qh3gQ',
        'UC7fk0CB07ly8oSl0aqKkqFg',
        'UCXTpFs_3PqI41qX2d9tL2Rw',
        'UCvzGlP9oQwU--Y0r9id_jnA',
        'UCp-5t9SrOQwXMU7iIjQfARg',
        'UCvaTdHTWBGv3MKj3KVqJVCw',
        'UChAnqc_AY5_I3Px5dig3X1Q',
        'UCvInZx9h3jC2JzsIzoOebWg',
        'UCdyqAaZDKHXg4Ahi7VENThQ',
        'UCCzUftO8KOVkV4wQG1vkUvg',
        'UC1DCedRgGHBdm81E1llLhOQ',
        'UCl_gCybOJRIgOXw6Qb4qJzQ',
        'UC5CwaMl1eIgY8h02uZw7u8A',
        'UCZlDXzGoo7d44bwdNObFacg',
        'UCS9uQI-jC3DE0L4IpXyvr6w',
        'UCqm3BQLlJfvkTsX_hvm0UmA',
        'UC1uv2Oq6kNxgATlCiez59hw',
        'UCa9Y57gfeY0Zro_noHRVrnw',
        'UCFKOVgVbGmX65RxO3EtH3iw',
        'UCAWSyEs_Io8MtpY3m-zqILA',
        'UCUKD-uaobj9jiqB-VXt71mA',
        'UCK9V2B22uJYu3N7eR_BT9QA',
        'UCJFZiqLMntJufDCHc6bQixg']

    # DB上のアイテムを読み込み
    db_id = get_db_id(ref_db)

    # 各チャンネルIDごとにXMLparseからDB追加までの処理を実行
    for channel_id in channelIdList:
        add_video_item(db_id, ref_db, channel_id, youtube)

    # delete_items_last_week(ref_db)
    # 処理後の時刻
    t2 = time.time()

    # 経過時間を表示
    elapsed_time = t2 - t1
    print(f"経過時間：{elapsed_time}")


def parse_xml(channel_id):
    rssUrl = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    try:
        with urllib.request.urlopen(rssUrl) as response:
            # UrlからXmlデータを取得しrootへ格納
            xmlData = response.read()
            root = ET.fromstring(xmlData)
            video_id_list = []
            last_week = get_last_week_date()

            # entryタグ内のvideoIDとpublishedAtを取得
            for r in root.findall('{http://www.w3.org/2005/Atom}entry'):

                vid = r[1].text
                published = r[6].text
                # 投稿時間が先週よりも前ならループ抜ける
                if published < last_week:
                    break
                video_id_list.append(vid)

            # 取得したvideoIdをカンマ区切り文字列にする
        videoIdList_str = ",".join(video_id_list)
        return videoIdList_str

    except urllib.error.HTTPError as e:
        print('HTTPError', channel_id, e.code)
    except urllib.error.URLError as e:
        print('URLError', channel_id, e.reason)


def get_last_week_date():
    # 現在のイギリス時間を取得
    utc_date = datetime.now(timezone.utc)
    # 一週間前のイギリス時間を取得
    utc_date_last_week = utc_date - relativedelta(weeks=1)
    # 一週間前のイギリス時間を%Y-%m-%dT%H:%M:%SZ形式の文字列に変換
    utc_date_last_week_format = utc_date_last_week.strftime('%Y-%m-%dT%H:%M:%SZ')

    return utc_date_last_week_format


# Videoアイテムの取得
def get_items_video(channel_id, youtube):
    # クォータ使い切った時とJSONを返却されなかったときの例外処理
    try:
        video_items = youtube.videos().list(
            part='snippet,liveStreamingDetails,statistics',
            id=f'{parse_xml(channel_id)}',
        ).execute()
        return video_items
    except googleapiclient.errors.HttpError as e:
        print('get_items_video', e)


# チャンネルアイテムの取得
def get_items_channel(channel_id, youtube):
    print('channelID', channel_id)
    try:
        channel_items = youtube.channels().list(
            part='snippet',
            id=f'{channel_id}'
        ).execute()
        for single in channel_items['items']:
            single_channel_item = single

        return single_channel_item

    except googleapiclient.errors.HttpError as e:
        print(e)
    except KeyError as e:
        print('get_items_channel:KeyError', e)


# FirestoreのドキュメントIDを取得
def get_db_id(rdb):
    id_list = []
    key_val = rdb.get()
    for key, val in key_val.items():
        id_list.append(key)
    return id_list


def create_data_format(video_item, channel_item, event_type):
    if event_type == 'live':
        live_data = {
            video_item['id']: {
                u'title': video_item['snippet']['title'],
                u'thumbnailUrl': video_item['snippet']['thumbnails']['high']['url'],
                u'startTime': video_item['liveStreamingDetails']['actualStartTime'],
                u'currentViewers': video_item['liveStreamingDetails']['concurrentViewers'],
                u'channelName': channel_item['snippet']['title'],
                u'channelIconUrl': channel_item['snippet']['thumbnails']['high']['url'],
                u'eventType': video_item['snippet']['liveBroadcastContent']
            }
        }
        return live_data
    elif event_type == 'upcoming':
        upcoming_data = {
            video_item['id']: {
                u'title': video_item['snippet']['title'],
                u'thumbnailUrl': video_item['snippet']['thumbnails']['high']['url'],
                u'scheduledStartTime': video_item['liveStreamingDetails']['scheduledStartTime'],
                u'channelName': channel_item['snippet']['title'],
                u'channelIconUrl': channel_item['snippet']['thumbnails']['high']['url'],
                u'eventType': video_item['snippet']['liveBroadcastContent']
            }
        }
        return upcoming_data
    elif event_type == 'none' and 'likeCount' in video_item['statistics']:
        none_data = {
            video_item['id']: {
                u'title': video_item['snippet']['title'],
                u'thumbnailUrl': video_item['snippet']['thumbnails']['high']['url'],
                u'publishedAt': video_item['snippet']['publishedAt'],
                u'viewCount': video_item['statistics']['viewCount'],
                u'likeCount': video_item['statistics']['likeCount'],
                u'channelName': channel_item['snippet']['title'],
                u'channelIconUrl': channel_item['snippet']['thumbnails']['high']['url'],
                u'eventType': video_item['snippet']['liveBroadcastContent']
            }
        }
        return none_data
    else:
        none_noLike_data = {
            video_item['id']: {
                u'title': video_item['snippet']['title'],
                u'thumbnailUrl': video_item['snippet']['thumbnails']['high']['url'],
                u'publishedAt': video_item['snippet']['publishedAt'],
                u'viewCount': video_item['statistics']['viewCount'],
                u'channelName': channel_item['snippet']['title'],
                u'channelIconUrl': channel_item['snippet']['thumbnails']['high']['url'],
                u'eventType': video_item['snippet']['liveBroadcastContent']
            }
        }
        return none_noLike_data


def add_video_item(id_list, rdb, channel_id, youtube):
    try:
        video_item = get_items_video(channel_id, youtube)['items']
        channel_item = get_items_channel(channel_id, youtube)

        # YouTubeAPIを使って取得したアイテムをFirestoreに追加
        for single_Video in video_item:
            print('videoID', single_Video['id'])
            event_type = single_Video['snippet']['liveBroadcastContent']

            # FirestoreのドキュメントIDとXmlから取得したIDを比較
            # 一致していれば一部の要素を更新
            if single_Video['id'] in id_list:
                update_item = create_data_format(single_Video, channel_item, event_type)
                rdb.update(update_item)
            # 不一致だった場合追加
            else:
                update_item = create_data_format(single_Video, channel_item, event_type)
                rdb.update(update_item)

    except TypeError as e:
        print(e)


main()
