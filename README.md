# astrbot_plugin_face_convert

把纯文字回复合并为单行，并以 25% 概率保留最多一个真实 QQ 小表情的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

## v1.1.0：单条文字与可选表情

- 在所有候选表情中取第一个，每轮只抽签一次；75% 的候选回复去掉全部表情，25% 保留一个。QQ Face 组件和 `/表情` 速记使用同一规则。
- 纯文字回复保持纯文字，不额外添加表情，因此总体带表情比例至多约 25%。
- 文字中的换行合并为空格，输出一个 Plain 组件，表情追加到同一消息末尾。
- 包含图片、引用或其他组件的消息沿用原结构。
- 在 AstrBot WebUI 关闭「分段回复」，让文字和可选表情一起发送；重新载入插件。
- 默认概率在 `main.py` 的 `FACE_PROBABILITY = 0.25` 修改。概率只作用于 QQ 小表情；人格已要求不用 Unicode emoji 或字符颜文字。
- 处理只扫描当前回复，时间复杂度 O(n)，不增加模型或网络请求。

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

实际发出的是单条「牛的时雨」文字，并以 25% 概率在同一消息中附加得意小表情。

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

本插件为「从 QQ 聊天记录蒸馏人格」工作流的基础设施之一：人格提示词压缩回复并选择可选 `/X` 候选，本插件负责合并文字、概率控制和表情转换。当前使用单条回复模式，请关闭 AstrBot「分段回复」。

## License

MIT
