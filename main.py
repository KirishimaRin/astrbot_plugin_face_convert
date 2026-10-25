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


@register(
    "astrbot_plugin_face_convert",
    "RINCyaro",
    "把 LLM 回复里的 /表情 速记（/得意 /呲牙 等）转换为真实 QQ 表情，仅 aiocqhttp/NapCat 生效",
    "1.0.0",
)
class FaceConvertPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.on_decorating_result()
    async def convert_faces(self, event: AstrMessageEvent):
        result = event.get_result()
        if result is None or not getattr(result, "chain", None):
            return
        new_chain = []
        changed = False
        for comp in result.chain:
            if comp.__class__.__name__ != "Plain":
                new_chain.append(comp)
                continue
            text = getattr(comp, "text", None) or ""
            if "/" not in text or not TOKEN_RE.search(text):
                new_chain.append(comp)
                continue
            changed = True
            pos = 0
            for m in TOKEN_RE.finditer(text):
                if m.start() > pos:
                    new_chain.append(Comp.Plain(text[pos : m.start()]))
                new_chain.append(Comp.Face(id=FACE_MAP[m.group(1)]))
                pos = m.end()
            if pos < len(text):
                new_chain.append(Comp.Plain(text[pos:]))
        if changed:
            result.chain.clear()
            result.chain.extend(new_chain)
