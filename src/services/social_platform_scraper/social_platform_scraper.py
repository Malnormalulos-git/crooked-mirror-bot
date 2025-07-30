from abc import ABC, abstractmethod

from src.services.social_platform_scraper.models import SocialPost, SocialPlatform


class SocialPlatformScraper(ABC):
    @staticmethod
    @abstractmethod
    async def get_post(post_identifier: str) -> SocialPost | None:
        """Fetches post data by identifier"""
        pass

    @staticmethod
    @abstractmethod
    def extract_post_id(url_or_id: str) -> str | None:
        """Extract post ID from URL or validate ID"""
        pass

    @staticmethod
    @abstractmethod
    def platform() -> SocialPlatform:
        """Return the platform this service handles"""
        pass

    @staticmethod
    @abstractmethod
    def format_post_info(post: SocialPost) -> str:
        pass