import re

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

xml_video_id = []
error_channel_id = []


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
        'UC1suqwovbL1kzsoaZgFZLKg',
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
        'UCJFZiqLMntJufDCHc6bQixg',
        'UCL_qhgtOy0dy1Agp8vkySQg',
        'UCHsx4Hqa-1ORjQTh9TYDhww',
        'UCyl1z3jo3XHR1riLFKG5UAg',
        'UCoSrY_IQQVpmIRZ9Xf-y93g',
        'UCMwGHR0BTZuLsmjY_NT5Pwg',
        'UCAoy6rzhSf4ydcYjJw3WoVg',
        'UCOyYb1c43VlX9rc_lT6NKQw',
        'UCP0BspO_AMEe3aQqqpo89Dg',
        'UChgTyjG-pdNvxxhdsXfHQ5Q',
        'UCYz_5n-uDuChHtLo7My1HnQ',
        'UC727SQYUvx5pDDGQpTICNWg',
        'UC8rcEBzJSleTkf_-agPM20g'
    ]

    # DB上のアイテムを読み込み
    db_id = get_db_id(ref_db)

    # 各チャンネルIDごとにXMLparseからDB追加までの処理を実行
    for channel_id in channelIdList:
        add_video_item(db_id, ref_db, channel_id, youtube)

    delete_video_item(db_id, ref_db)

    xml_video_id.clear()

    # delete_items_last_week(ref_db)
    print(len(xml_video_id))
    # 処理後の時刻
    t2 = time.time()

    # 経過時間を表示
    elapsed_time = t2 - t1
    print(f"経過時間：{elapsed_time}")


def parse_xml(channel_id):
    rssUrl = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(rssUrl, None, headers)
    print('parse_xml')
    try:
        with urllib.request.urlopen(req) as response:
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
                xml_video_id.append(vid)

            # 取得したvideoIdをカンマ区切り文字列にする
        videoIdList_str = ",".join(video_id_list)
        return videoIdList_str

    except urllib.error.HTTPError as e:
        print('HTTPError', channel_id, e.code)
        error_channel_id.append(channel_id)
    except urllib.error.URLError as e:
        print('URLError', channel_id, e.reason)
        error_channel_id.append(channel_id)


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
    print('get_items_video')
    # クォータ使い切った時とJSONを返却されなかったときの例外処理
    try:
        video_items = youtube.videos().list(
            part='snippet,liveStreamingDetails,statistics,contentDetails',
            id=f'{parse_xml(channel_id)}',
        ).execute()
        return video_items
    except googleapiclient.errors.HttpError as e:
        print('get_items_video', e)
        error_channel_id.append(channel_id)


# チャンネルアイテムの取得
def get_items_channel(channel_id, youtube):
    print('channelID', channel_id)
    single_channel_item = None
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
        error_channel_id.append(channel_id)
    except KeyError as e:
        print('get_items_channel:KeyError', e)
        error_channel_id.append(channel_id)


# FirestoreのドキュメントIDを取得
def get_db_id(rdb):
    print('get_db_id')
    id_list = []
    key_val = rdb.get()
    for key, val in key_val.items():
        id_list.append(key)
    return id_list


# 動画のタグ付け
def add_category_tag(video_title, video_category):
    pattern_sing = 'sing|歌枠'
    pattern_chat = 'chat|freetalk|雑談|スパチャ'
    pattern_watch_along = 'WATCHALONG|同時視聴'
    pattern_birthday = 'BIRTHDAY|生誕祭'
    pattern_song = 'オリジナル曲|original song'
    pattern_drawing = 'drawing'

    results_sing = re.search(pattern_sing, video_title, re.IGNORECASE)
    results_chat = re.search(pattern_chat, video_title, re.IGNORECASE)
    results_watch_along = re.search(pattern_watch_along, video_title, re.IGNORECASE)
    results_birthday = re.search(pattern_birthday, video_title, re.IGNORECASE)
    results_song = re.search(pattern_song, video_title, re.IGNORECASE)
    results_drawing = re.search(pattern_drawing, video_title, re.IGNORECASE)

    if results_sing:
        return 'sing'
    elif results_chat:
        return 'chat'
    elif results_watch_along:
        return 'watchAlong'
    elif results_birthday:
        return 'birthday'
    elif results_song:
        return 'song'
    elif results_drawing:
        return 'drawing'
    elif video_category == '20':
        return 'game'


def create_data_format(video_item, channel_item, event_type, video_tag):
    video_id = video_item['id']
    video_title = video_item['snippet']['title']
    thumbnail_url = video_item['snippet']['thumbnails']['high']['url']

    channel_id = video_item['snippet']['channelId']
    channel_name = channel_item['snippet']['title']
    channel_icon_url = channel_item['snippet']['thumbnails']['high']['url']

    if event_type == 'live':
        start_time = video_item['liveStreamingDetails']['actualStartTime']
        current_viewers = video_item['liveStreamingDetails']['concurrentViewers']
        if 'concurrentViewers' in video_item['liveStreamingDetails']:
            live_data = {
                video_id: {
                    u'title': video_title,
                    u'thumbnailUrl': thumbnail_url,
                    u'startTime': start_time,
                    u'currentViewers': current_viewers,
                    u'channelId': channel_id,
                    u'channelName': channel_name,
                    u'channelIconUrl': channel_icon_url,
                    u'eventType': event_type,
                    u'tag': video_tag
                }
            }
            return live_data
        # プレミアム公開中の動画（視聴者数が取得できない）
        elif 'concurrentViewers' not in video_item['liveStreamingDetails']:
            live_premium_data = {
                video_id: {
                    u'title': video_title,
                    u'thumbnailUrl': thumbnail_url,
                    u'startTime': start_time,
                    u'currentViewers': 'プレミアム公開中',
                    u'channelId': channel_id,
                    u'channelName': channel_name,
                    u'channelIconUrl': channel_icon_url,
                    u'eventType': event_type,
                    u'tag': video_tag
                }
            }
            return live_premium_data

    elif event_type == 'upcoming':
        scheduled_start_time = video_item['liveStreamingDetails']['scheduledStartTime']
        upcoming_data = {
            video_id: {
                u'title': video_title,
                u'thumbnailUrl': thumbnail_url,
                u'scheduledStartTime': scheduled_start_time,
                u'channelId': channel_id,
                u'channelName': channel_name,
                u'channelIconUrl': channel_icon_url,
                u'eventType': event_type,
                u'tag': video_tag
            }
        }
        return upcoming_data

    elif event_type == 'none':
        published_at = video_item['snippet']['publishedAt']
        view_count = video_item['statistics']['viewCount']
        like_count = video_item['statistics']['likeCount']
        duration = video_item['contentDetails']['duration']
        if 'likeCount' in video_item['statistics']:
            none_data = {
                video_id: {
                    u'title': video_title,
                    u'thumbnailUrl': thumbnail_url,
                    u'publishedAt': published_at,
                    u'viewCount': view_count,
                    u'likeCount': like_count,
                    u'channelId': channel_id,
                    u'channelName': channel_name,
                    u'channelIconUrl': channel_icon_url,
                    u'eventType': event_type,
                    u'duration': duration,
                    u'tag': video_tag
                }
            }
            return none_data
        # 評価非表示の場合
        if 'likeCount' not in video_item['statistics']:
            none_hide_data = {
                video_id: {
                    u'title': video_title,
                    u'thumbnailUrl': thumbnail_url,
                    u'publishedAt': published_at,
                    u'viewCount': view_count,
                    u'likeCount': 'None',
                    u'channelId': channel_id,
                    u'channelName': channel_id,
                    u'channelIconUrl': channel_icon_url,
                    u'eventType': event_type,
                    u'tag': video_tag
                }
            }
            return none_hide_data


# RealtimeDatabaseに書き込み
def add_video_item(id_list, rdb, channel_id, youtube):
    print('add_video_item')
    try:
        video_item = get_items_video(channel_id, youtube)['items']
        channel_item = get_items_channel(channel_id, youtube)

        # YouTubeAPIを使って取得したアイテムをFirestoreに追加
        for single_Video in video_item:
            # print('videoID', single_Video['id'])
            event_type = single_Video['snippet']['liveBroadcastContent']
            video_tag = add_category_tag(single_Video['snippet']['title'], single_Video['snippet']['categoryId'])

            update_item = create_data_format(single_Video, channel_item, event_type, video_tag)
            rdb.update(update_item)

    except TypeError as e:
        print(e)


def delete_video_item(db_id, rdb):
    print('db', len(db_id), db_id)
    print('xml', len(xml_video_id), xml_video_id)
    # 一週間以上まえのアイテムのみ抽出
    did = set(db_id).difference(set(xml_video_id))
    print('did', did)
    for d in did:
        db_channelId = rdb.child(f'{d}').child('channelId').get()
        # dbから取得したアイテムのチャンネルIDがエラーが発生したチャンネルIDリストの中に含まれていなければ削除
        if db_channelId not in set(error_channel_id):
            print('delete', f'{d}')
            rdb.child(f'{d}').delete()


main()
