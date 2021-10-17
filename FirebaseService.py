import firebase_admin
import googleapiclient
from firebase_admin import credentials
from firebase_admin import db
import os
from os.path import join, dirname
from dotenv import load_dotenv


class FirebaseService:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not firebase_admin._apps:
        print('初期化')
        cred = credentials.Certificate('hologram-firebase-adminsdk.json')

        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL,
        })

    ref_db = db.reference('/video')

    def __init__(self, video_item):
        self.video_item = video_item

    # FirestoreのドキュメントIDを取得
    def get_db_id(self):
        print('get_db_id')
        id_list = []
        key_val = self.ref_db.get()
        for key, val in key_val.items():
            id_list.append(key)
        return id_list

    def write_video_item(self):
        print("FirebaseService", "write")
        self.ref_db.update(self.video_items)


    # def delete_video_item(db_id, rdb):
    #     print('db', len(db_id), db_id)
    #     print('xml', len(xml_video_id), xml_video_id)
    #     # 一週間以上まえのアイテムのみ抽出
    #     did = set(db_id).difference(set(xml_video_id))
    #     print('did', did)
    #     for d in did:
    #         db_channelId = rdb.child(f'{d}').child('channelId').get()
    #         # dbから取得したアイテムのチャンネルIDがエラーが発生したチャンネルIDリストの中に含まれていなければ削除
    #         if db_channelId not in set(error_channel_id):
    #             print('delete', f'{d}')
    #             rdb.child(f'{d}').delete()
