"""Shared types for the content pipeline."""

from dataclasses import dataclass, field
from enum import Enum


class Platform(str, Enum):
    DOUYIN = "douyin"
    BILIBILI = "bilibili"
    XIAOHONGSHU = "xiaohongshu"
    KUAISHOU = "kuaishou"
    TENCENT = "tencent"
    BAIJIAHAO = "baijiahao"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


PLATFORM_NAMES = {
    Platform.DOUYIN: "抖音",
    Platform.BILIBILI: "B站",
    Platform.XIAOHONGSHU: "小红书",
    Platform.KUAISHOU: "快手",
    Platform.TENCENT: "视频号",
    Platform.BAIJIAHAO: "百家号",
    Platform.TIKTOK: "TikTok",
    Platform.YOUTUBE: "YouTube",
}


@dataclass
class ContentExport:
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    platform_hint: str = "article"


@dataclass
class PublishRequest:
    platform: Platform
    account_name: str
    content: ContentExport
    video_file: str | None = None
    image_files: list[str] = field(default_factory=list)
    schedule: str | None = None
