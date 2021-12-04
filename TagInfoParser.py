import re


class TagInfoParser:

    def __init__(self, title, category, desc, channel_name):
        self.title = title
        self.category = category
        self.desc = desc
        self.channel_name = channel_name

    # 配信カテゴリのタグ付
    def add_category_tag(self):
        print("taginfo_category")
        pattern_sing = 'sing|歌枠|KARAOKE'
        pattern_chat = 'chat|freetalk|supa|雑談|スパチャ|スーパーチャット|Donation Reading'
        pattern_watch_along = 'WATCHALONG|同時視聴|WATCH-A-LONG'
        pattern_birthday = 'BIRTHDAY|生誕祭'
        pattern_song = 'オリジナル曲|original song|original'
        pattern_drawing = 'drawing'
        pattern_live = 'LIVE'
        pattern_cover = '歌ってみた|cover'
        pattern_asmr = 'ASMR|A　S　M　R'
        pattern_cooking = 'Cooking'
        pattern_membership = 'メン限|member'

        results_sing = re.search(pattern_sing, self.title, re.IGNORECASE)
        results_chat = re.search(pattern_chat, self.title, re.IGNORECASE)
        results_watch_along = re.search(pattern_watch_along, self.title, re.IGNORECASE)
        results_birthday = re.search(pattern_birthday, self.title, re.IGNORECASE)
        results_song = re.search(pattern_song, self.title, re.IGNORECASE)
        results_drawing = re.search(pattern_drawing, self.title, re.IGNORECASE)
        results_live = re.search(pattern_live, self.title)
        results_cover = re.search(pattern_cover, self.title)
        results_asmr = re.search(pattern_asmr, self.title, re.IGNORECASE)
        results_cooking = re.search(pattern_cooking, self.title)
        results_membership = re.search(pattern_membership, self.title, re.IGNORECASE)

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
        elif self.category == '20':
            return 'game'
        elif results_live:
            return 'live'
        elif results_cover:
            return 'cover'
        elif results_asmr:
            return 'ASMR'
        elif results_cooking:
            return 'cooking'
        elif results_membership:
            return 'membership'

    # 出演メンバーのタグ付
    def add_member_tag(self):
        pattern_all_mem = "ときのそら|AZKi|ロボ子|さくらみこ|白上フブキ|夏色まつり|夜空メル|赤井はあと|" \
                          "アキ・ローゼンタール|アキロゼ|湊あくあ|癒月ちょこ|百鬼あやめ|紫咲シオン|大空スバル|大神ミオ" \
                          "|猫又おかゆ|戌神ころね|不知火フレア|白銀ノエル|宝鐘マリン|兎田ぺこら|潤羽るしあ|星街すいせい|Suisei" \
                          "|天音かなた|桐生ココ|角巻わため|常闇トワ|姫森ルーナ|雪花ラミィ|桃鈴ねね|獅白ぼたん|尾丸ポルカ" \
                          "|ラプラス・ダークネス|鷹嶺ルイ|博衣こより|沙花叉クロヱ|風真いろは"\
                          "|IOFI|MOONA|ムーナ|Risu|Ollie|Anya|Reine|" \
                          "Calliope|Kiara|Ina'nis|Gura|Amelia|IRyS|" \
                          "hololive ホロライブ |" \
                          "Sana|Fauna|Kronii|Mumei|Baelz|" \
                          "花咲みやび|奏手イヅル|アルランディス|律可|アステル|岸堂天真|夕刻ロベル|影山シエン|荒咬オウガ"

        pattern_split = "Don't forget to follow and subscribe to my sisters!|" \
                        "Don't forget to follow Ollie's sisters!!!|" \
                        "Mohon bantuannya ya, untuk teman seperjuangannya Iofi~!|" \
                        "~ Hololive Indonesia ~|Support the other holoID gen 2 girls!|holoID!!|" \
                        "｡.｡:|＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝|『百花繚乱花吹雪』|◆2020.12.29『曇天羊／角巻わため|" \
                        "Relay|ーーーーーーーーーーーーーーーーーーー|" \
                        "ーーー▼花咲みやびのがいよう▼ーーー|【ホロスターズ1期生】|▼△▼|【お知らせ】|ーーー|----------|【ホロスターズ1期生の先輩たち】|" \
                        "★★★|✧✧✧|----------------------|≫ ──── ≪•◦ ❈ ◦•≫ ──── ≪|««-------------- ≪ °◇◆◇° ≫ --------------»»|" \
                        "✦••┈┈┈••┈┈┈••✦••┈┈┈••┈┈┈••✦|￥*⇔*――"

        """
        概要欄から正規表現に一致するものがあれば分割し、
        その中からチャンネル名に一致するものを検索

        一致しない場合はそのまま概要欄からチャンネル名に一致するものを検索
        """
        if re.search(pattern_split, self.desc):
            split_desc = re.split(pattern_split, self.desc)[0]
            tag_all_mem = re.findall(pattern_all_mem, split_desc)
        else:
            tag_all_mem = re.findall(pattern_all_mem, self.desc)

        # self.channel_name = YoutubeService.get_items_channel(channel_id, youtube)['snippet']['title']
        print(self.channel_name)
        # 投稿者を必ずタグに含めるために、チャンネル名からパターンに一致するものを検索しタグに追加
        result_channel_name = re.findall(pattern_all_mem, self.channel_name, re.IGNORECASE)
        tag_all_mem.extend(result_channel_name)

        # チャンネル名に一致したものと概要欄の中から一致したチャンネル名の2つが含まれていた場合いづれかを削除
        if {'星街すいせい', 'Suisei'} <= set(tag_all_mem):
            tag_all_mem.remove('星街すいせい')
        elif {'IOFI', 'Iofi'} <= set(tag_all_mem):
            tag_all_mem.remove('IOFI')
        else:
            pass

        return ",".join(set(tag_all_mem))
        # print(",".join(set(tag_all_mem)))

    # グループのタグ付
    def add_group_tag(self):
        holo_Jp = 'holoJp'
        holo_En = 'holoEn'
        holo_Id = 'holoId'
        holo_stars = 'holoStars'

        pattern_holo_jp = "ときのそら|AZKi|ロボ子|さくらみこ|白上フブキ|夏色まつり|夜空メル|赤井はあと|" \
                          "アキ・ローゼンタール|アキロゼ|湊あくあ|癒月ちょこ|百鬼あやめ|紫咲シオン|大空スバル|大神ミオ" \
                          "|猫又おかゆ|戌神ころね|不知火フレア|白銀ノエル|宝鐘マリン|兎田ぺこら|潤羽るしあ|Suisei" \
                          "|天音かなた|桐生ココ|角巻わため|常闇トワ|姫森ルーナ|雪花ラミィ|桃鈴ねね|獅白ぼたん|尾丸ポルカ" \
                          "|ラプラス・ダークネス|鷹嶺ルイ|博衣こより|沙花叉クロヱ|風真いろは"

        pattern_holo_en = "Calliope|Kiara|Ina'nis|Gura|Amelia|IRyS|Sana|Fauna|Kronii|Mumei|Baelz"

        pattern_holo_id = "Iofi|Moona|Risu|Ollie|Anya|Reine"

        pattern_holo_stars = "花咲みやび|奏手イヅル|アルランディス|律可|アステル|岸堂天真|夕刻ロベル|影山シエン|荒咬オウガ"

        # channel_name = YoutubeService.get_items_channel()['snippet']['title']

        if re.search(pattern_holo_jp, self.channel_name):
            return holo_Jp
        elif re.search(pattern_holo_en, self.channel_name):
            return holo_En
        elif re.search(pattern_holo_id, self.channel_name):
            return holo_Id
        elif re.search(pattern_holo_stars, self.channel_name):
            return holo_stars
        else:
            return 'none'
