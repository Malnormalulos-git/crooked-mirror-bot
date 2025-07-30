from dataclasses import dataclass
from enum import Enum

from twitter.scraper import Scraper
import asyncio
from concurrent.futures import ThreadPoolExecutor

from twitter.util import find_key, parse_card_media

from config_reader import config
import logging

class MediaType(Enum):
    IMAGE = 0,
    VIDEO = 1,

@dataclass(frozen=True)
class MediaItem:
    type: MediaType
    url: str

class Tweet:
    __scraper: Scraper = None
    __executor = ThreadPoolExecutor(max_workers=4)

    @staticmethod
    def __get_scraper() -> Scraper:
        if Tweet.__scraper is None:
            cookies = {
                "ct0": config.twitter_ct0,
                "auth_token": config.twitter_auth_token
            }
            Tweet.__scraper = Scraper(cookies=cookies, save=False)

        return Tweet.__scraper

    def __get_tweet_data(self, tweet_id: str) -> list[dict]:
        """Synchronous function to run in thread pool"""
        scraper = self.__get_scraper()

        meta_data = scraper.tweets_by_ids([tweet_id])

        return meta_data

    def __init__(self, tweet_id: str) -> None:
        self.id = tweet_id
        self.ok = False
        self.text = None
        self.author = None
        self.created_at = None
        self.stats = None
        self.media = None

    async def load_data(self) -> bool:
        """Async method for loading tweets data"""
        try:
            loop = asyncio.get_event_loop()
            meta_data = await loop.run_in_executor(
                self.__executor, 
                self.__get_tweet_data, 
                self.id
            )

            # ------------------from-scrapper-(https://pypi.org/project/twitter-api-client/)-------------------
            media_meta_data = {}
            for tweet in meta_data[0].get('data', {}).get('tweetResult', []):
                root = tweet.get('result', {}).get('tweet', {}) or tweet.get('result', {})
                if _id := root.get('rest_id'):
                    date = root.get('legacy', {}).get('created_at', '')
                    uid = root.get('legacy', {}).get('user_id_str', '')
                    media_meta_data[_id] = {'date': date, 'uid': uid, 'img': set(),
                                  'video': {'thumb': set(), 'video_info': {}, 'hq': set()}, 'card': []}
                    for _media in (y for x in find_key(root, 'media') for y in x if isinstance(x, list)):
                        if vinfo := _media.get('video_info'):
                            hq = sorted(vinfo.get('variants', []), key=lambda x: -x.get('bitrate', 0))[0]['url']
                            media_meta_data[_id]['video']['video_info'] |= vinfo
                            media_meta_data[_id]['video']['hq'].add(hq)
                        if (url := _media.get('media_url_https', '')) and "_video_thumb" not in url:
                            url = f'{url}?name=orig'
                            media_meta_data[_id]['img'].add(url)
                    if card := root.get('card', {}).get('legacy', {}):
                        media_meta_data[_id]['card'].extend(card.get('binding_values', []))

            media: set[MediaItem] = set()
            for k, v in media_meta_data.items():
                media.update({MediaItem(MediaType.IMAGE, im) for im in v['img']})
                media.update({MediaItem(MediaType.VIDEO, vid) for vid in v['video']['hq']})
                media.update({MediaItem(MediaType.IMAGE, parse_card_media(im)) for im in v['card']})
            # ------------------from-scrapper-(https://pypi.org/project/twitter-api-client/)-------------------

        except Exception as e:
            logging.error(f"Error while scraping tweet: {e}")
            return False

        try:
            result = meta_data[0]['data']['tweetResult'][0]['result']
            legacy = result['legacy']
            user = result['core']['user_results']['result']['legacy']

            tweet_text = legacy['full_text']
            author_name = user['name']
            screen_name = user['screen_name']
            created_at = legacy['created_at']

            likes = legacy['favorite_count']
            retweets = legacy['retweet_count']
            replies = legacy['reply_count']
            views = result.get('views', {}).get('count', 'N/A')

            self.ok = True
            self.text = tweet_text
            self.author = f"{author_name} (@{screen_name})"
            self.created_at = created_at
            self.stats = {
                'likes': likes,
                'retweets': retweets,
                'replies': replies,
                'views': views,
            }
            self.media = media
            return True
        except Exception as e:
            logging.error(f"Error while extracting tweet info: {e}")
            return False

    @classmethod
    async def create(cls, tweet_id: str) -> 'Tweet':
        """Async class method for creation and initialization of object"""
        tweet = cls(tweet_id)
        await tweet.load_data()
        return tweet

    def __repr__(self):
        if self.ok:
            return f"""
👤 Author: {self.author}
📅 Date: {self.created_at}

📝 Text:\n{self.text}

📊 Stats:
❤️ {self.stats['likes']:,} likes
🔄 {self.stats['retweets']:,} retweets  
💬 {self.stats['replies']:,} replies
👁️ {self.stats['views']} views

🆔 Tweet ID: {self.id}
🖼️ Media items: {len(self.media)}
"""
        return f"❌ Could not extract tweet ({self.id}) information"