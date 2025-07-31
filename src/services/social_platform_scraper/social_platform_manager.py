from typing import Dict

from src.services.social_platform_scraper.models import SocialPlatform, SocialPost
from src.services.social_platform_scraper.social_platform_scraper import SocialPlatformScraper
from src.services.social_platform_scraper.twitter_scraper import TwitterScraper


class SocialPlatformManager:
    """Manager for handling different social media services"""

    def __init__(self):
        self._services: Dict[SocialPlatform, SocialPlatformScraper] = {
            SocialPlatform.TWITTER: TwitterScraper(),
            # SocialPlatform.FACEBOOK: FacebookScraper(),
            # SocialPlatform.INSTAGRAM: InstagramScraper(),
        }

    def detect_platform(self, url_or_id: str) -> SocialPlatform | None:
        """Detect social media platform from URL"""
        url_lower = url_or_id.lower()

        if 'twitter.com' in url_lower or 'x.com' in url_lower:
            return SocialPlatform.TWITTER
        # elif 'facebook.com' in url_lower:
        #     return SocialPlatform.FACEBOOK
        # elif 'instagram.com' in url_lower:
        #     return SocialPlatform.INSTAGRAM

        # If no platform detected, try Twitter as default (for pure id)
        twitter_service = self._services[SocialPlatform.TWITTER]
        if twitter_service.extract_post_id(url_or_id):
            return SocialPlatform.TWITTER

        return None

    async def get_post(self, url_or_id: str) -> SocialPost | None:
        """Get post from any supported platform"""
        platform = self.detect_platform(url_or_id)
        if not platform:
            return None

        service = self._services[platform]
        post_id = service.extract_post_id(url_or_id)
        if not post_id:
            return None

        return await service.get_post(post_id)

    def get_service(self, platform: SocialPlatform) -> SocialPlatformScraper | None:
        """Get service for specific platform"""
        return self._services.get(platform)

    def format_post_info(self, post: SocialPost) -> str:
        """Format post info for its platform"""
        service = self.get_service(post.platform)
        return service.format_post_info(post)