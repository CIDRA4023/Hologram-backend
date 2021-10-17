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

from XmlParser import XmlParser

# xml_video_id = []
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
        # 'UC-hM6YJuNYVAmUWxeIr9FeA',
        # 'UCdn5BQ06XqgXoAxIhbqw5Rg',
        # 'UCQ0UDLQCjY0rmuxCDE38FGg',
        # 'UCD8HOxPs4Xvsm8H0ZxXGiBw',
        # 'UC1CfXB_kRs3C-zaeTG3oGyg',
        # 'UCFTLzh12_nrtzqBPsTCqenA',
        # 'UC1opHUrw8rvnsadT-iGp7Cg',
        # 'UC1suqwovbL1kzsoaZgFZLKg',
        # 'UC7fk0CB07ly8oSl0aqKkqFg',
        # 'UCXTpFs_3PqI41qX2d9tL2Rw',
        # 'UCvzGlP9oQwU--Y0r9id_jnA',
        # 'UCp-5t9SrOQwXMU7iIjQfARg',
        # 'UCvaTdHTWBGv3MKj3KVqJVCw',
        # 'UChAnqc_AY5_I3Px5dig3X1Q',
        # 'UCvInZx9h3jC2JzsIzoOebWg',
        # 'UCdyqAaZDKHXg4Ahi7VENThQ',
        # 'UCCzUftO8KOVkV4wQG1vkUvg',
        # 'UC1DCedRgGHBdm81E1llLhOQ',
        # 'UCl_gCybOJRIgOXw6Qb4qJzQ',
        # 'UC5CwaMl1eIgY8h02uZw7u8A',
        # 'UCZlDXzGoo7d44bwdNObFacg',
        # 'UCS9uQI-jC3DE0L4IpXyvr6w',
        # 'UCqm3BQLlJfvkTsX_hvm0UmA',
        # 'UC1uv2Oq6kNxgATlCiez59hw',
        # 'UCa9Y57gfeY0Zro_noHRVrnw',
        # 'UCFKOVgVbGmX65RxO3EtH3iw',
        # 'UCAWSyEs_Io8MtpY3m-zqILA',
        # 'UCUKD-uaobj9jiqB-VXt71mA',
        # 'UCK9V2B22uJYu3N7eR_BT9QA',
        # 'UCJFZiqLMntJufDCHc6bQixg',
        # 'UCL_qhgtOy0dy1Agp8vkySQg',
        # 'UCHsx4Hqa-1ORjQTh9TYDhww',
        # 'UCyl1z3jo3XHR1riLFKG5UAg',
        # 'UCoSrY_IQQVpmIRZ9Xf-y93g',
        # 'UCMwGHR0BTZuLsmjY_NT5Pwg',
        # 'UCAoy6rzhSf4ydcYjJw3WoVg',
        # 'UCOyYb1c43VlX9rc_lT6NKQw',
        # 'UCP0BspO_AMEe3aQqqpo89Dg',
        # 'UChgTyjG-pdNvxxhdsXfHQ5Q',
        # 'UCYz_5n-uDuChHtLo7My1HnQ',
        # 'UC727SQYUvx5pDDGQpTICNWg',
        # 'UC8rcEBzJSleTkf_-agPM20g',
        #
        # 'UC6t3-_N8A6ME1JShZHHqOMw',
        # 'UCZgOv3YDEs-ZnZWDYVwJdmA',
        # 'UCKeAhJvy8zgXWbh9duVjIaQ',
        # 'UC9mf_ZVpouoILRY9NUIaK-w',
        # 'UCNVEsYbiZjH5QLmGeSgTSzg',
        # 'UCGNI4MENvnsymYjKiZwv9eg',
        # 'UCANDOlYTJT7N5jlRC3zfzVA',
        # 'UChSvpZYRPh0FvG4SJGSga3g',
        # 'UCwL7dgTxKo8Y4RFIKWaf8gA',
        # 'UCsUj0dszADCGbF3gNrQEuSQ',
        # 'UCO_aKKYxn4tvrqPjcTzZ6EQ',
        # 'UCmbs8T6MWqUHP1tIQvSgKrg',
        # 'UC3n5uGu18FoCy23ggWWp8tA',
        # 'UCgmPnx-EEeOrZSg5Tiw7ZRQ'
    ]

    # DB上のアイテムを読み込み
    db_id = get_db_id(ref_db)

    # 各チャンネルIDごとにXMLparseからDB追加までの処理を実行
    for single_channel_id in channelIdList:
        # XmlParserから今週アップロードされた動画を取得
        xml_parse = XmlParser(channel_id=single_channel_id)
        xml_video_id = xml_parse.parse_xml()

        add_video_item(db_id, ref_db, single_channel_id, youtube, xml_video_id)

    # delete_video_item(db_id, ref_db)

    # リストに格納したリストデータを削除
    xml_video_id_list = XmlParser.xml_video_id_list

    xml_video_id_list.clear()
    print(len(xml_video_id_list))
    print(XmlParser.error_channel_id_list)
    # delete_items_last_week(ref_db)

    # 処理後の時刻
    t2 = time.time()

    # 経過時間を表示
    elapsed_time = t2 - t1
    print(f"経過時間：{elapsed_time}")


# Videoアイテムの取得
def get_items_video(channel_id, youtube, xml_video_id):
    print('get_items_video')
    # クォータ使い切った時とJSONを返却されなかったときの例外処理
    print(f'{xml_video_id}')
    try:
        video_items = youtube.videos().list(
            part='snippet,liveStreamingDetails,statistics,contentDetails',
            id=f'{xml_video_id}',
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


# # 動画のタグ付け
# def add_category_tag(video_title, video_category):
#     pattern_sing = 'sing|歌枠|KARAOKE'
#     pattern_chat = 'chat|freetalk|supa|雑談|スパチャ|スーパーチャット|Donation Reading'
#     pattern_watch_along = 'WATCHALONG|同時視聴|WATCH-A-LONG'
#     pattern_birthday = 'BIRTHDAY|生誕祭'
#     pattern_song = 'オリジナル曲|original song|original'
#     pattern_drawing = 'drawing'
#     pattern_live = 'LIVE'
#     pattern_cover = '歌ってみた|cover'
#     pattern_asmr = 'ASMR|A　S　M　R'
#     pattern_cooking = 'Cooking'
#     pattern_membership = 'メン限|member'
# 
#     results_sing = re.search(pattern_sing, video_title, re.IGNORECASE)
#     results_chat = re.search(pattern_chat, video_title, re.IGNORECASE)
#     results_watch_along = re.search(pattern_watch_along, video_title, re.IGNORECASE)
#     results_birthday = re.search(pattern_birthday, video_title, re.IGNORECASE)
#     results_song = re.search(pattern_song, video_title, re.IGNORECASE)
#     results_drawing = re.search(pattern_drawing, video_title, re.IGNORECASE)
#     results_live = re.search(pattern_live, video_title)
#     results_cover = re.search(pattern_cover, video_title)
#     results_asmr = re.search(pattern_asmr, video_title, re.IGNORECASE)
#     results_cooking = re.search(pattern_cooking, video_title)
#     results_membership = re.search(pattern_membership, video_title, re.IGNORECASE)
# 
#     if results_sing:
#         return 'sing'
#     elif results_chat:
#         return 'chat'
#     elif results_watch_along:
#         return 'watchAlong'
#     elif results_birthday:
#         return 'birthday'
#     elif results_song:
#         return 'song'
#     elif results_drawing:
#         return 'drawing'
#     elif video_category == '20':
#         return 'game'
#     elif results_live:
#         return 'live'
#     elif results_cover:
#         return 'cover'
#     elif results_asmr:
#         return 'ASMR'
#     elif results_cooking:
#         return 'cooking'
#     elif results_membership:
#         return 'membership'
# 
# 
# def add_member_tag(desc, channel_id, youtube):
#     pattern_all_mem = "ときのそら|AZKi|ロボ子|さくらみこ|白上フブキ|夏色まつり|夜空メル|赤井はあと|" \
#                       "アキ・ローゼンタール|アキロゼ|湊あくあ|癒月ちょこ|百鬼あやめ|紫咲シオン|大空スバル|大神ミオ" \
#                       "|猫又おかゆ|戌神ころね|不知火フレア|白銀ノエル|宝鐘マリン|兎田ぺこら|潤羽るしあ|星街すいせい|Suisei" \
#                       "|天音かなた|桐生ココ|角巻わため|常闇トワ|姫森ルーナ|雪花ラミィ|桃鈴ねね|獅白ぼたん|尾丸ポルカ" \
#                       "|IOFI|MOONA|ムーナ|Risu|Ollie|Anya|Reine|" \
#                       "Calliope|Kiara|Ina'nis|Gura|Amelia|IRyS|" \
#                       "hololive ホロライブ |" \
#                       "Sana|Fauna|Kronii|Mumei|Baelz|" \
#                       "花咲みやび|奏手イヅル|アルランディス|律可|アステル|岸堂天真|夕刻ロベル|影山シエン|荒咬オウガ"
# 
#     pattern_split = "Don't forget to follow and subscribe to my sisters!|" \
#                     "Don't forget to follow Ollie's sisters!!!|" \
#                     "Mohon bantuannya ya, untuk teman seperjuangannya Iofi~!|" \
#                     "~ Hololive Indonesia ~|Support the other holoID gen 2 girls!|holoID!!|" \
#                     "｡.｡:|＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝|『百花繚乱花吹雪』|◆2020.12.29『曇天羊／角巻わため|" \
#                     "Relay|ーーーーーーーーーーーーーーーーーーー|" \
#                     "ーーー▼花咲みやびのがいよう▼ーーー|【ホロスターズ1期生】|▼△▼|【お知らせ】|ーーー|----------|【ホロスターズ1期生の先輩たち】|" \
#                     "★★★|✧✧✧|----------------------|≫ ──── ≪•◦ ❈ ◦•≫ ──── ≪|««-------------- ≪ °◇◆◇° ≫ --------------»»"
# 
#     """
#     概要欄から正規表現に一致するものがあれば分割し、
#     その中からチャンネル名に一致するものを検索
# 
#     一致しない場合はそのまま概要欄からチャンネル名に一致するものを検索
#     """
#     if re.search(pattern_split, desc):
#         split_desc = re.split(pattern_split, desc)[0]
#         tag_all_mem = re.findall(pattern_all_mem, split_desc)
#     else:
#         tag_all_mem = re.findall(pattern_all_mem, desc)
# 
#     channel_name = get_items_channel(channel_id, youtube)['snippet']['title']
#     print(channel_name)
#     # 配信、投稿動画のチャンネル名をパターンに一致するものを検索しタグに追加
#     result_channel_name = re.findall(pattern_all_mem, channel_name, re.IGNORECASE)
#     tag_all_mem.extend(result_channel_name)
# 
#     # チャンネル名に一致したものと概要欄の中から一致したチャンネル名の2つが含まれていた場合いづれかを削除
#     if {'星街すいせい', 'Suisei'} <= set(tag_all_mem):
#         tag_all_mem.remove('星街すいせい')
#     elif {'IOFI', 'Iofi'} <= set(tag_all_mem):
#         tag_all_mem.remove('IOFI')
#     else:
#         pass
# 
#     return ",".join(set(tag_all_mem))
#     # print(",".join(set(tag_all_mem)))
# 
# 
# def add_group_tag(channel_id, youtube):
#     holo_Jp = 'holoJp'
#     holo_En = 'holoEn'
#     holo_Id = 'holoId'
#     holo_stars = 'holoStars'
# 
#     pattern_holo_jp = "ときのそら|AZKi|ロボ子|さくらみこ|白上フブキ|夏色まつり|夜空メル|赤井はあと|" \
#                       "アキ・ローゼンタール|アキロゼ|湊あくあ|癒月ちょこ|百鬼あやめ|紫咲シオン|大空スバル|大神ミオ" \
#                       "|猫又おかゆ|戌神ころね|不知火フレア|白銀ノエル|宝鐘マリン|兎田ぺこら|潤羽るしあ|Suisei" \
#                       "|天音かなた|桐生ココ|角巻わため|常闇トワ|姫森ルーナ|雪花ラミィ|桃鈴ねね|獅白ぼたん|尾丸ポルカ"
# 
#     pattern_holo_en = "Calliope|Kiara|Ina'nis|Gura|Amelia|IRyS|Sana|Fauna|Kronii|Mumei|Baelz"
# 
#     pattern_holo_id = "Iofi|Moona|Risu|Ollie|Anya|Reine"
# 
#     pattern_holo_stars = "花咲みやび|奏手イヅル|アルランディス|律可|アステル|岸堂天真|夕刻ロベル|影山シエン|荒咬オウガ"
# 
#     channel_name = get_items_channel(channel_id, youtube)['snippet']['title']
# 
#     if re.search(pattern_holo_jp, channel_name):
#         return holo_Jp
#     elif re.search(pattern_holo_en, channel_name):
#         return holo_En
#     elif re.search(pattern_holo_id, channel_name):
#         return holo_Id
#     elif re.search(pattern_holo_stars, channel_name):
#         return holo_stars
#     else:
#         return 'none'


def create_data_format(video_item, channel_item, event_type, tag_category, tag_member, tag_group, tag_platform):
    video_id = video_item['id']
    video_title = video_item['snippet']['title']
    thumbnail_url = video_item['snippet']['thumbnails']['high']['url']

    channel_id = video_item['snippet']['channelId']
    channel_name = channel_item['snippet']['title']
    channel_icon_url = channel_item['snippet']['thumbnails']['high']['url']

    if event_type == 'live':
        start_time = video_item['liveStreamingDetails']['actualStartTime']

        if 'concurrentViewers' in video_item['liveStreamingDetails']:
            current_viewers = video_item['liveStreamingDetails']['concurrentViewers']
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
                    u'tag': {
                        'category': tag_category,
                        'member': tag_member,
                        'group': tag_group,
                        'platform': tag_platform
                    }
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
                    u'tag': {
                        'category': tag_category,
                        'member': tag_member,
                        'group': tag_group,
                        'platform': tag_platform
                    }
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
                u'tag': {
                    'category': tag_category,
                    'member': tag_member,
                    'group': tag_group,
                    'platform': tag_platform
                }
            }
        }
        return upcoming_data

    elif event_type == 'none':
        published_at = video_item['snippet']['publishedAt']
        view_count = video_item['statistics']['viewCount']

        duration = video_item['contentDetails']['duration']
        if 'likeCount' in video_item['statistics']:
            like_count = video_item['statistics']['likeCount']
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
                    u'tag': {
                        'category': tag_category,
                        'member': tag_member,
                        'group': tag_group,
                        'platform': tag_platform
                    }
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
                    u'tag': {
                        'category': tag_category,
                        'member': tag_member,
                        'group': tag_group,
                        'platform': tag_platform
                    }
                }
            }
            return none_hide_data


# RealtimeDatabaseに書き込み
def add_video_item(id_list, rdb, channel_id, youtube, xml_video_id):
    print('add_video_item')
    try:
        video_item = get_items_video(channel_id, youtube, xml_video_id)['items']
        channel_item = get_items_channel(channel_id, youtube)

        # YouTubeAPIを使って取得したアイテムをFirestoreに追加
        for single_Video in video_item:
            print('videoID', single_Video['id'])
            event_type = single_Video['snippet']['liveBroadcastContent']
            event_type = single_Video['snippet']['liveBroadcastContent']
            tag_category = add_category_tag(single_Video['snippet']['title'], single_Video['snippet']['categoryId'])
            tag_member = add_member_tag(single_Video['snippet']['description'], channel_id, youtube)
            tag_group = add_group_tag(channel_id, youtube)
            tag_platform = 'youtube'

            update_item = create_data_format(single_Video, channel_item, event_type, tag_category, tag_member,
                                             tag_group, tag_platform)
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
