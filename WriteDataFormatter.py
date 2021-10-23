class WriteDataFormatter:

    def __init__(self, video_item, channel_item, event_type, tag_category, tag_member, tag_group, tag_platform):
        self.video_item = video_item
        self.channel_item = channel_item
        self.event_type = event_type
        self.tag_category = tag_category
        self.tag_member = tag_member
        self.tag_group = tag_group
        self.tag_platform = tag_platform

    def create_data_format(self):
        video_id = self.video_item['id']
        video_title = self.video_item['snippet']['title']
        thumbnail_url = self.video_item['snippet']['thumbnails']['high']['url']

        channel_id = self.video_item['snippet']['channelId']
        channel_name = self.channel_item['snippet']['title']
        channel_icon_url = self.channel_item['snippet']['thumbnails']['high']['url']

        # 配信中のアイテムの書き込みデータ構造
        if self.event_type == 'live':
            start_time = self.video_item['liveStreamingDetails']['actualStartTime']
            current_viewers = ''
            if 'concurrentViewers' in self.video_item['liveStreamingDetails']:
                current_viewers = self.video_item['liveStreamingDetails']['concurrentViewers']
                live_data = {
                    video_id: {
                        u'title': video_title,
                        u'thumbnailUrl': thumbnail_url,
                        u'startTime': start_time,
                        u'currentViewers': current_viewers,
                        u'channelId': channel_id,
                        u'channelName': channel_name,
                        u'channelIconUrl': channel_icon_url,
                        u'eventType': self.event_type,
                        u'tag': {
                            'category': self.tag_category,
                            'member': self.tag_member,
                            'group': self.tag_group,
                            'platform': self.tag_platform
                        }
                    }
                }
                return live_data
            # プレミアム公開中の動画（視聴者数が取得できない）
            elif 'concurrentViewers' not in self.video_item['liveStreamingDetails']:
                # プレミアム公開動画の再生数は「premiere」とする
                current_viewers = 'premiere'
                live_premiere_data = {
                    video_id: {
                        u'title': video_title,
                        u'thumbnailUrl': thumbnail_url,
                        u'startTime': start_time,
                        u'currentViewers': current_viewers,
                        u'channelId': channel_id,
                        u'channelName': channel_name,
                        u'channelIconUrl': channel_icon_url,
                        u'eventType': self.event_type,
                        u'tag': {
                            'category': self.tag_category,
                            'member': self.tag_member,
                            'group': self.tag_group,
                            'platform': self.tag_platform
                        }
                    }
                }
                return live_premiere_data

        # 配信予定の書き込みデータ構造
        elif self.event_type == 'upcoming':
            scheduled_start_time = self.video_item['liveStreamingDetails']['scheduledStartTime']
            upcoming_data = {
                video_id: {
                    u'title': video_title,
                    u'thumbnailUrl': thumbnail_url,
                    u'scheduledStartTime': scheduled_start_time,
                    u'channelId': channel_id,
                    u'channelName': channel_name,
                    u'channelIconUrl': channel_icon_url,
                    u'eventType': self.event_type,
                    u'tag': {
                        'category': self.tag_category,
                        'member': self.tag_member,
                        'group': self.tag_group,
                        'platform': self.tag_platform
                    }
                }
            }
            return upcoming_data

        # アーカイブの書き込みデータ構造
        elif self.event_type == 'none':
            published_at = self.video_item['snippet']['publishedAt']
            view_count = self.video_item['statistics']['viewCount']

            duration = self.video_item['contentDetails']['duration']
            like_count = ''

            if 'likeCount' in self.video_item['statistics']:
                like_count = self.video_item['statistics']['likeCount']
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
                        u'eventType': self.event_type,
                        u'duration': duration,
                        u'tag': {
                            'category': self.tag_category,
                            'member': self.tag_member,
                            'group': self.tag_group,
                            'platform': self.tag_platform
                        }
                    }
                }
                return none_data
            # 評価非表示の場合
            if 'likeCount' not in self.video_item['statistics']:
                like_count = 'None'
                none_hide_data = {
                    video_id: {
                        u'title': video_title,
                        u'thumbnailUrl': thumbnail_url,
                        u'publishedAt': published_at,
                        u'viewCount': view_count,
                        u'likeCount': like_count,
                        u'channelId': channel_id,
                        u'channelName': channel_id,
                        u'channelIconUrl': channel_icon_url,
                        u'eventType': self.event_type,
                        u'tag': {
                            'category': self.tag_category,
                            'member': self.tag_member,
                            'group': self.tag_group,
                            'platform': self.tag_platform
                        }
                    }
                }
                return none_hide_data
