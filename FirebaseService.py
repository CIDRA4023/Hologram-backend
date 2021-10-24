import firebase_admin
import googleapiclient
from firebase_admin import credentials
from firebase_admin import db
import os
from os.path import join, dirname
from dotenv import load_dotenv
from XmlParser import XmlParser


class FirebaseService:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not firebase_admin._apps:
        print('初期化')
        cred = credentials.Certificate('hologram-test-firebase-adminsdk.json')

        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
        })

    ref_db = db.reference('/video')

    def __init__(self, video_item):
        self.video_item = video_item

    # FirestoreのドキュメントIDを取得
    def get_db_id(self):
        print("FirebaseService", 'get_db_id')
        id_list = []
        key_val = self.ref_db.get()
        # DB上に書き込まれたアイテムのvideoIdを取得
        for key, val in key_val.items():
            id_list.append(key)
        return id_list
    
    # 
    def write_video_item(self):
        print("FirebaseService", "write_video_item")
        self.ref_db.update(self.video_item)

    def delete_video_item(self, update_db_items, xml_video_ids, error_channel_ids):
        print("FirebaseService", 'update_db_items', len(update_db_items), update_db_items)
        print("FirebaseService", 'xml_video_ids', len(xml_video_ids), xml_video_ids)
        print("FirebaseService", 'error_channel_ids', len(error_channel_ids), error_channel_ids)
        
        # 一週間以上まえのアイテムのみ抽出
        # （更新後のDB上のアイテム）-（XMLで取得したアイテム）
        last_week_ids = set(update_db_items).difference(set(xml_video_ids))
        print('last_week_ids', last_week_ids)
        for single_id in last_week_ids:
            db_channelId = self.ref_db.child(f'{single_id}').child('channelId').get()
            print('db_channel_id', db_channelId)
            # dbから取得したアイテムのチャンネルIDがエラーが発生したチャンネルIDリストの中に含まれていなければ削除
            # xml_parseで取得できなかったチャンネルの動画情報が削除されてしまうため
            if db_channelId not in set(error_channel_ids):
                print('delete', f'{single_id}')
                self.ref_db.child(f'{single_id}').delete()
