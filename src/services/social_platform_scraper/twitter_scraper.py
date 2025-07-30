import asyncio
import logging
import re
from concurrent.futures import ThreadPoolExecutor

from twitter.scraper import Scraper
from twitter.util import find_key, parse_card_media
from config_reader import config
from src.services.social_platform_scraper.models import SocialPost, SocialPlatform, PostStats, MediaItem, MediaType
from src.services.social_platform_scraper.social_platform_scraper import SocialPlatformScraper


class TwitterScraper(SocialPlatformScraper):
    __scraper: Scraper = None
    __executor = ThreadPoolExecutor(max_workers=4)

    @staticmethod
    async def get_post(post_identifier: str) -> SocialPost | None:
        try:
            loop = asyncio.get_event_loop()
            meta_data = await loop.run_in_executor(
                TwitterScraper.__executor,
                TwitterScraper.__get_tweet_data,
                post_identifier
            )

            media = TwitterScraper.__extract_media(meta_data)

            result = meta_data[0]['data']['tweetResult'][0]['result']
            legacy = result['legacy']
            user = result['core']['user_results']['result']['legacy']

            return SocialPost(
                id=post_identifier,
                platform=TwitterScraper.platform(),
                text=legacy['full_text'],
                author=f"{user['name']} (@{user['screen_name']})",
                created_at=legacy['created_at'],
                stats=PostStats(
                    likes=legacy['favorite_count'],
                    shares=legacy['retweet_count'],
                    comments=legacy['reply_count'],
                    views=result.get('views', {}).get('count', 'N/A')
                ),
                media=media
            )

        except Exception as e:
            logging.error(f"Error while extracting tweet info {post_identifier}: {e}")
            return None

    @staticmethod
    def extract_post_id(link_or_id: str) -> str | None:
        pattern = r'(?:.*status/)?(\d+)'
        match = re.search(pattern, link_or_id)
        if not match:
            return None

        tweet_id = match.group(1)
        return tweet_id

    @staticmethod
    def platform() -> SocialPlatform:
        return SocialPlatform.TWITTER


    @staticmethod
    def format_post_info(post: SocialPost) -> str:
        return f"""
👤 Author: {post.author}
📅 Date: {post.created_at}

📝 Text:\n{post.text}

📊 Stats:
❤️ {post.stats.likes:,} likes
🔄 {post.stats.shares:,} retweets  
💬 {post.stats.comments:,} replies
👁️ {post.stats.views} views

🆔 Tweet ID: {post.id}
🖼️ Media items: {len(post.media)}
"""

    @staticmethod
    def __get_scraper() -> Scraper:
        if TwitterScraper.__scraper is None:
            cookies = {
                "ct0": config.twitter_ct0,
                "auth_token": config.twitter_auth_token
            }
            TwitterScraper.__scraper = Scraper(cookies=cookies, save=False)

        return TwitterScraper.__scraper

    @staticmethod
    def __get_tweet_data(tweet_id: str) -> list[dict]:
        """Synchronous function to run in thread pool"""
        scraper = TwitterScraper.__get_scraper()

        meta_data = scraper.tweets_by_ids([tweet_id])

        return meta_data

    @staticmethod
    def __extract_media(meta_data: list[dict]) -> set[MediaItem]:
    # ------------------from-scrapper-(https://pypi.org/project/twitter-api-client/)-------------------
        media_meta_data = {}

        for tweet in meta_data[0].get('data', {}).get('tweetResult', []):
            root = tweet.get('result', {}).get('tweet', {}) or tweet.get('result', {})
            if _id := root.get('rest_id'):
                date = root.get('legacy', {}).get('created_at', '')
                uid = root.get('legacy', {}).get('user_id_str', '')
                media_meta_data[_id] = {
                    'date': date, 'uid': uid, 'img': set(),
                    'video': {'thumb': set(), 'video_info': {}, 'hq': set()},
                    'card': []
                }

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

        return media
