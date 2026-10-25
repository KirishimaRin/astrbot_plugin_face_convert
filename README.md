# astrbot_plugin_face_convert

把 LLM 回复里的 `/表情` 速记转换成真实 QQ 小表情的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

## 为什么需要它

聊天导出工具（如 QQ Chat Exporter）会把真人发的 QQ 小表情渲染成 `/得意`、`/呲牙` 这样的文本速记。直接让 LLM 模仿这种文风时，bot 输出的 `/得意` 只会以纯文本发出——QQ 客户端不会把它变成表情。本插件在消息发送前（`on_decorating_result` 钩子）把白名单内的速记替换为真正的 `Face` 消息段。

## 安装

把本仓库克隆到 AstrBot 的插件目录：

```bash
cd astrbot/data/plugins
git clone https://github.com/KirishimaRin/astrbot_plugin_face_convert
```

然后在 WebUI → 插件管理 中重载（或重启 AstrBot）。无需任何配置。

## 使用

LLM 回复里出现速记即自动转换，例如模型输出：

```
牛的时雨
/得意
```

实际发出的是「牛的时雨」文本 + 得意小表情。

## 支持的表情

face id 取自 [QFace](https://github.com/koishijs/QFace) 的 QQNT 官方表情索引（537 个表情），与聊天导出语料中的速记一一对应：

| 速记 | id | 速记 | id |
| --- | --- | --- | --- |
| /得意 | 4 | /可怜 | 111 |
| /流泪 | 5 | /魔鬼笑 | 286 |
| /呲牙 | 13 | /大怨种 | 344 |
| /偷笑 | 20 | /偷感 | 427 |
| /抓狂 | 18 | /点赞（/赞） | 76 |
| /骷髅 | 37 | /捂脸 | 264 |
| /微笑 | 14 | /冷汗 | 96 |

增删表情改 `main.py` 里的 `FACE_MAP` 即可（新表情的 id 在 QFace 索引 `_index.v2.json` 里查 `describe` 字段）。

## 注意

- 仅 `aiocqhttp` 平台（NapCat / Lagrange 等 OneBot 实现）生效，`Face` 组件是 QQ 专有消息段。
- go-cqhttp 旧文档与 QQ 官方 bot 文档的 face id 是**不同的编号体系**，请勿混用本表。
- 白名单精确匹配 `/词语`，URL 中的 `/` 不会误伤。
- 个别较新的动态表情（偷感、大怨种等）在老版本 PC 客户端可能不渲染，按需从 `FACE_MAP` 删除即可回退为文本。

## 配套人格

本插件为「从 QQ 聊天记录蒸馏人格」工作流的基础设施之一：人格提示词让模型按真人语料输出 `/X` 速记，本插件负责还原成表情。搭配 AstrBot「分段回复」（换行拆分 + 短间隔）可获得接近真人的连发节奏。

## License

MIT
