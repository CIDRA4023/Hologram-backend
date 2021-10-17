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
from TagInfoParser import TagInfoParser
from YoutubeService import YoutubeService
from FirebaseService import FirebaseService

# xml_video_id = []
error_channel_id = []


def main():
    # 処理前の時刻
    t1 = time.time()

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
    firebase = FirebaseService(video_items="")
    firebase.get_db_id()

    # 各チャンネルIDごとにXMLparseからDB追加までの処理を実行
    for single_channel_id in channelIdList:
        # YoutubeServiceのインスタンス生成
        youtube = YoutubeService(channel_id=single_channel_id)

        add_video_item(youtube)

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
def add_video_item(youtube):
    print('add_video_item')
    try:
        video_item = youtube.get_items_video()['items']
        # channel_item = get_items_channel(channel_id, youtube)

        # YouTubeAPIを使って取得したアイテムをFirestoreに追加
        for single_Video in video_item:
            print('MainVideoID', single_Video['id'])
            event_type = single_Video['snippet']['liveBroadcastContent']

            title = single_Video['snippet']['title']
            category = single_Video['snippet']['categoryId']
            desc = single_Video['snippet']['description']

            channel_item = youtube.get_items_channel()
            channel_name = youtube.get_items_channel()['snippet']['title']
            tag = TagInfoParser(title=title, category=category, desc=desc, channel_name=channel_name)

            tag_category = tag.add_category_tag()
            tag_member = tag.add_member_tag()
            tag_group = tag.add_group_tag()
            tag_platform = 'youtube'
            print(tag_category, tag_member, tag_group)
            update_item = create_data_format(single_Video, channel_item, event_type, tag_category, tag_member,
                                             tag_group, tag_platform)

            firebase = FirebaseService(video_item=update_item)
            firebase.write_video_item()


    except TypeError as e:
        print(e)


main()
