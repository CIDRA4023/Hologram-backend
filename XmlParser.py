import urllib
from urllib import request
import xml.etree.ElementTree as ET
from datetime import timezone, datetime
from dateutil.relativedelta import relativedelta


class XmlParser:
    # Xmlから取得した全てのVideoIDリスト
    xml_video_id_list = []
    # エラーが発生して取得できなかったチャンネルIDリスト
    error_channel_id_list = set([])

    def __init__(self, channel_id):
        self.channel_id = channel_id

    @staticmethod
    def get_last_week_date():
        # 現在のイギリス時間を取得
        utc_date = datetime.now(timezone.utc)
        # 一週間前のイギリス時間を取得
        utc_date_last_week = utc_date - relativedelta(weeks=1)
        # 一週間前のイギリス時間を%Y-%m-%dT%H:%M:%SZ形式の文字列に変換
        utc_date_last_week_format = utc_date_last_week.strftime('%Y-%m-%dT%H:%M:%SZ')

        return utc_date_last_week_format
    
    def parse_xml(self):
        # 各チャンネルのRSSフィードを取得
        rssUrl = f'https://www.youtube.com/feeds/videos.xml?channel_id={self.channel_id}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        req = urllib.request.Request(rssUrl, None, headers)

        print('parse_xml')
        try:
            with urllib.request.urlopen(req) as response:
                # UrlからXmlデータを取得しrootへ格納
                xmlData = response.read()
                root = ET.fromstring(xmlData)
                video_id_list = []
                last_week_date = self.get_last_week_date()

                # entryタグ内のvideoIDとpublishedAtを取得
                for r in root.findall('{http://www.w3.org/2005/Atom}entry'):

                    single_video_id = r[1].text
                    published_date = r[6].text
                    # 投稿時間が先週よりも前ならループ抜ける
                    if published_date < last_week_date:
                        break
                    video_id_list.append(single_video_id)
                    self.xml_video_id_list.append(single_video_id)

            # 取得したvideoIdをカンマ区切り文字列にする
            formatted_video_id = ",".join(video_id_list)
            print(self.xml_video_id_list)
            return formatted_video_id

        # エラーが発生した際はそのチャンネルIDをリストに格納
        except urllib.error.HTTPError as e:
            print('HTTPError', self.channel_id, e.code)
            self.error_channel_id_list.add(self.channel_id)
        except urllib.error.URLError as e:
            print('URLError', channel_id, e.reason)
            self.error_channel_id_list.add(self.channel_id)
