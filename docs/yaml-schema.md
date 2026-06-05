# 小说转剧本 YAML Schema

## 1. 设计目标

该 Schema 用于描述由小说改编而来的结构化剧本初稿。它需要同时满足作者可读、程序可解析、后续可编辑三个目标。

选择 YAML 的原因是：YAML 比 JSON 更适合人工阅读和修改，适合剧本这类文本密集型内容；同时它仍然保留结构化数据能力，方便后端校验、前端编辑和未来工具链扩展。

## 2. 顶层结构

```yaml
metadata: {}
source: {}
characters: []
locations: []
scenes: []
notes: []
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| metadata | object | 是 | 剧本元信息 |
| source | object | 是 | 原小说来源信息 |
| characters | array | 是 | 人物列表 |
| locations | array | 是 | 地点列表 |
| scenes | array | 是 | 场景列表 |
| notes | array | 否 | AI 生成或作者修改建议 |

## 3. metadata

```yaml
metadata:
  title: "雨夜来信"
  genre: "悬疑"
  language: "zh-CN"
  version: "1.0"
  logline: "一名编辑在雨夜收到来自失踪作者的手稿。"
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| title | string | 是 | 剧本标题 |
| genre | string | 否 | 类型，如悬疑、爱情、奇幻 |
| language | string | 是 | 语言代码，默认 zh-CN |
| version | string | 是 | Schema 或剧本版本 |
| logline | string | 否 | 一句话故事梗概 |

设计原因：元信息独立存放，方便页面展示、文件命名、版本管理和后续导入其他剧本工具。

## 4. source

```yaml
source:
  chapter_count: 3
  chapter_titles:
    - "第一章 雨夜"
    - "第二章 手稿"
    - "第三章 旧书店"
```

设计原因：剧本改编需要能追溯原小说章节。保留章节标题和数量，可以帮助作者定位某一场戏来自哪一段原文。

## 5. characters

```yaml
characters:
  - id: "char_001"
    name: "林晚"
    role: "protagonist"
    description: "年轻编辑，谨慎但好奇。"
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | string | 是 | 人物唯一标识 |
| name | string | 是 | 人物姓名 |
| role | string | 否 | protagonist、supporting、antagonist 等 |
| description | string | 否 | 人物简介 |

设计原因：人物使用独立 ID，而不是只靠姓名引用，可以避免重名、别名和称呼变化造成混乱，也方便后续做人物关系图。

## 6. locations

```yaml
locations:
  - id: "loc_001"
    name: "旧书店"
    description: "藏在巷尾的二层书店，灯光昏黄。"
```

设计原因：地点独立建表，方便统计场景使用频率，也方便剧本制作阶段进行置景和拍摄计划管理。

## 7. scenes

```yaml
scenes:
  - id: "scene_001"
    title: "雨夜的手稿"
    chapter_refs:
      - "第一章 雨夜"
    location_id: "loc_001"
    time_of_day: "night"
    characters:
      - "char_001"
    summary: "林晚在旧书店收到神秘手稿。"
    beats:
      - type: "action"
        content: "雨水沿着玻璃门滑落，林晚推门走进旧书店。"
      - type: "dialogue"
        speaker_id: "char_001"
        content: "这份手稿是谁留下的？"
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| id | string | 是 | 场景唯一标识 |
| title | string | 是 | 场景标题 |
| chapter_refs | array | 是 | 来源章节 |
| location_id | string | 否 | 地点 ID |
| time_of_day | string | 否 | morning、day、evening、night 等 |
| characters | array | 是 | 登场人物 ID |
| summary | string | 否 | 场景概要 |
| beats | array | 是 | 剧情节拍 |

设计原因：剧本的基本单位是场景。通过场景 ID、章节引用、地点、时间和人物列表，可以把小说叙事转化为可编辑、可排练、可制作的剧本结构。

## 8. beats

`beats` 是场景内最小的剧本内容单位。

支持类型：

| type | 说明 |
| --- | --- |
| action | 动作或舞台说明 |
| dialogue | 人物对白 |
| narration | 旁白或画外音 |
| transition | 转场 |
| sound | 声音提示 |
| shot | 镜头建议 |

```yaml
beats:
  - type: "action"
    content: "林晚停在书架前，听见楼上传来脚步声。"
  - type: "dialogue"
    speaker_id: "char_001"
    content: "有人在吗？"
  - type: "transition"
    content: "切至二楼走廊。"
```

设计原因：小说文本通常混合叙述、心理、环境和对白。使用 `beats` 可以把这些内容拆成可调整的剧本单位，让作者后续容易增删、移动和重写。

## 9. 完整示例

```yaml
metadata:
  title: "雨夜来信"
  genre: "悬疑"
  language: "zh-CN"
  version: "1.0"
  logline: "一名编辑在雨夜收到来自失踪作者的手稿。"
source:
  chapter_count: 3
  chapter_titles:
    - "第一章 雨夜"
    - "第二章 手稿"
    - "第三章 旧书店"
characters:
  - id: "char_001"
    name: "林晚"
    role: "protagonist"
    description: "年轻编辑，谨慎但好奇。"
locations:
  - id: "loc_001"
    name: "旧书店"
    description: "藏在巷尾的二层书店，灯光昏黄。"
scenes:
  - id: "scene_001"
    title: "雨夜的手稿"
    chapter_refs:
      - "第一章 雨夜"
    location_id: "loc_001"
    time_of_day: "night"
    characters:
      - "char_001"
    summary: "林晚在旧书店收到神秘手稿。"
    beats:
      - type: "action"
        content: "雨水沿着玻璃门滑落，林晚推门走进旧书店。"
      - type: "dialogue"
        speaker_id: "char_001"
        content: "这份手稿是谁留下的？"
notes:
  - "初稿保留悬疑节奏，后续可强化人物动机。"
```

