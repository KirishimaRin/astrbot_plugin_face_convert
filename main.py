import math
import random
import re

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

# QQNT 官方表情索引（QFace 库 _index.v2.json）的 emojiId
FACE_MAP = {
    "得意": 4,
    "流泪": 5,
    "呲牙": 13,
    "偷笑": 20,
    "抓狂": 18,
    "骷髅": 37,
    "赞": 76,
    "点赞": 76,
    "可怜": 111,
    "魔鬼笑": 286,
    "大怨种": 344,
    "偷感": 427,
    "微笑": 14,
    "捂脸": 264,
    "冷汗": 96,
}
# 长词在前，避免 "点赞" 被 "赞" 抢先匹配出残字
TOKEN_RE = re.compile(
    "/(" + "|".join(sorted(FACE_MAP, key=len, reverse=True)) + ")"
)
DEFAULT_FACE_PERCENT = 25


@register(
    "astrbot_plugin_face_convert",
    "RINCyaro",
    "合并单行回复，按后台设置的概率保留最多一个 QQ 表情",
    "1.2.0",
)
class FaceConvertPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    def _face_probability(self) -> float:
        try:
            percent = float(self.config.get("face_probability_percent", DEFAULT_FACE_PERCENT))
        except (TypeError, ValueError, OverflowError):
            return DEFAULT_FACE_PERCENT / 100
        if not math.isfinite(percent):
            return DEFAULT_FACE_PERCENT / 100
        return max(0.0, min(100.0, percent)) / 100

    @filter.on_decorating_result()
    async def convert_faces(self, event: AstrMessageEvent):
        result = event.get_result()
        if result is None or not getattr(result, "chain", None):
            return
        texts = []
        faces = []
        other_components = []
        for comp in result.chain:
            if isinstance(comp, Comp.Face):
                faces.append(comp)
                continue
            if not isinstance(comp, Comp.Plain):
                other_components.append(comp)
                continue
            text = comp.text or ""
            faces.extend(Comp.Face(id=FACE_MAP[m.group(1)]) for m in TOKEN_RE.finditer(text))
            texts.append(TOKEN_RE.sub("", text))

        # 媒体、引用、工具结果沿用原消息结构，只处理纯文字/QQ 表情回复。
        if other_components:
            return
        text = " ".join(" ".join(texts).split()).strip()
        new_chain = [Comp.Plain(text)] if text else []
        if faces and random.random() < self._face_probability():
            new_chain.append(faces[0])
        result.chain.clear()
        result.chain.extend(new_chain)
