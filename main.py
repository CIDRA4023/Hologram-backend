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
from WriteDataFormatter import WriteDataFormatter


def main():
    # 処理前の時刻
    t1 = time.time()

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
        'UC8rcEBzJSleTkf_-agPM20g',

        'UC6t3-_N8A6ME1JShZHHqOMw',
        'UCZgOv3YDEs-ZnZWDYVwJdmA',
        'UCKeAhJvy8zgXWbh9duVjIaQ',
        'UC9mf_ZVpouoILRY9NUIaK-w',
        'UCNVEsYbiZjH5QLmGeSgTSzg',
        'UCGNI4MENvnsymYjKiZwv9eg',
        'UCANDOlYTJT7N5jlRC3zfzVA',
        'UChSvpZYRPh0FvG4SJGSga3g',
        'UCwL7dgTxKo8Y4RFIKWaf8gA',
        'UCsUj0dszADCGbF3gNrQEuSQ',
        'UCO_aKKYxn4tvrqPjcTzZ6EQ',
        'UCmbs8T6MWqUHP1tIQvSgKrg',
        'UC3n5uGu18FoCy23ggWWp8tA',
        'UCgmPnx-EEeOrZSg5Tiw7ZRQ'
    ]

    # 各チャンネルIDごとにXMLparseからDB追加までの処理を実行
    for single_channel_id in channelIdList:
        # XmlParserから今週アップロードされた動画を取得
        xml_parse = XmlParser(channel_id=single_channel_id)
        xml_video_ids = xml_parse.get_xml_videos()
        # YoutubeServiceのインスタンス生成
        youtube = YoutubeService(xml_video_ids=xml_video_ids, channel_id=single_channel_id)
        add_video_item(youtube)

    # YoutubeDataApiでエラーが発生したチャンネルID
    youtube_error_ids = YoutubeService.error_channel_ids
    print('youtube_error', youtube_error_ids)
    # XML解析時にエラーが発生したチャンネルID
    xml_error_ids = XmlParser.error_channel_id_list
    print('xml_error', xml_error_ids)
    # エラーが発生したチャンネルIDを結合
    error_channel_ids = youtube_error_ids | xml_error_ids
    print('ErrorID', error_channel_ids)

    # 更新後のDB上のアイテムを読み込み
    firebase = FirebaseService(video_item="")
    update_db_items = firebase.get_db_id()
    xml_video_ids = XmlParser.xml_video_ids
    # DB更新後に1周間以上前のアイテムがあったら削除
    firebase.delete_video_item(update_db_items, xml_video_ids, error_channel_ids)

    # XMLから取得したリストデータを削除
    xml_video_ids = XmlParser.xml_video_ids
    xml_video_ids.clear()

    # 処理後の時刻
    t2 = time.time()

    # 経過時間を表示
    elapsed_time = t2 - t1
    print(f"経過時間：{elapsed_time}")


# RealtimeDatabaseに書き込み
def add_video_item(youtube):
    print('add_video_item')
    try:
        video_items = youtube.get_items_video()['items']

        # YouTubeAPIを使って取得したアイテムをFirestoreに追加
        for video_item in video_items:
            print('MainVideoID', video_item['id'])

            # Youtubeから動画、チャンネル情報を取得
            event_type = video_item['snippet']['liveBroadcastContent']
            title = video_item['snippet']['title']
            category = video_item['snippet']['categoryId']
            desc = video_item['snippet']['description']
            channel_item = youtube.get_items_channel()
            channel_name = youtube.get_items_channel()['snippet']['title']

            # タグ情報を作成
            tag = TagInfoParser(title=title, category=category, desc=desc, channel_name=channel_name)
            tag_category = tag.add_category_tag()
            tag_member = tag.add_member_tag()
            tag_group = tag.add_group_tag()
            tag_platform = 'youtube'

            print(tag_category, tag_member, tag_group)
            write_format = WriteDataFormatter(video_item=video_item, channel_item=channel_item, event_type=event_type,
                                              tag_category=tag_category, tag_member=tag_member, tag_group=tag_group,
                                              tag_platform=tag_platform)
            update_item = write_format.create_data_format()
            print('Update_Item', update_item)

            # DBへ書き込み
            firebase = FirebaseService(video_item=update_item)
            firebase.write_video_item()

    except TypeError as e:
        print(e)


main()
