import random
import re

import astrbot.api.message_components as Comp
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
# 有表情候选的回复，每轮只抽一次；纯文字回复不强加表情。
FACE_PROBABILITY = 0.25


@register(
    "astrbot_plugin_face_convert",
    "RINCyaro",
    "合并单行回复，并以 25% 概率保留最多一个 QQ 表情",
    "1.1.0",
)
class FaceConvertPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

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
        if faces and random.random() < FACE_PROBABILITY:
            new_chain.append(faces[0])
        result.chain.clear()
        result.chain.extend(new_chain)
