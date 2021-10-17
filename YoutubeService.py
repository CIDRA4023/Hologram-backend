from XmlParser import XmlParser
import googleapiclient
from googleapiclient.discovery import build
import os
from os.path import join, dirname
from dotenv import load_dotenv


class YoutubeService:
    # APIキーを入力してYoutubeインスタンスを生成
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_KEY")
    YOUTUBE_API_KEY = YOUTUBE_API_KEY
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # エラーが発生して取得できなかったチャンネルIDリスト
    error_channel_ids = []

    def __init__(self, channel_id):
        self.channel_id = channel_id

    # Videoアイテムの取得
    def get_items_video(self):

        # XmlParserから今週アップロードされた動画を取得
        xml_parse = XmlParser(channel_id=self.channel_id)
        xml_video_id = xml_parse.parse_xml()
        print('get_items_video')

        # クォータ使い切った時とJSONを返却されなかったときの例外処理
        print("YoutubeService", f'{xml_video_id}')
        try:
            video_items = self.youtube.videos().list(
                part='snippet,liveStreamingDetails,statistics,contentDetails',
                id=f'{xml_video_id}',
            ).execute()
            print("YoutubeService", video_items)
            return video_items
        except googleapiclient.errors.HttpError as e:
            print('get_items_video', e)
            error_channel_ids.append(channel_id)

    # チャンネルアイテムの取得
    def get_items_channel(self):
        print('channelID', self.channel_id)
        channel_item = None
        try:
            channel_items = self.youtube.channels().list(
                part='snippet',
                id=f'{self.channel_id}'
            ).execute()
            for single in channel_items['items']:
                channel_item = single

            return channel_item

        except googleapiclient.errors.HttpError as e:
            print(e)
            error_channel_ids.append(self.channel_id)
        except KeyError as e:
            print('get_items_channel:KeyError', e)
            error_channel_id.append(self.channel_id)
