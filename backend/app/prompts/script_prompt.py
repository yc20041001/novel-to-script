from app.models import NovelChapter


SYSTEM_PROMPT = """你是专业编剧助手，擅长把中文小说改编为结构化剧本初稿。
请严格输出合法 JSON，不要输出 Markdown、解释文字或代码块。
输出 JSON 必须符合给定字段结构。
"""


def build_script_prompt(chapters: list[NovelChapter]) -> str:
    chapter_text = "\n\n".join(
        f"## {index + 1}. {chapter.title}\n{chapter.content}"
        for index, chapter in enumerate(chapters)
    )

    return f"""请将以下至少 3 个章节的小说文本改编成结构化剧本初稿。

要求：
1. 生成可继续编辑的剧本结构。
2. 按场景拆分，不要只做摘要。
3. 将小说叙事转换为 action、dialogue、narration、transition、sound、shot 等 beats。
4. 每个人物必须有稳定 id，例如 char_001。
5. 每个地点必须有稳定 id，例如 loc_001。
6. 每个场景必须有稳定 id，例如 scene_001，并保留 chapter_refs。
7. dialogue 类型 beat 如果能确定说话人，必须填写 speaker_id。
8. 只输出 JSON，不能输出 YAML 或其他解释。

JSON 结构：
{{
  "metadata": {{
    "title": "剧本标题",
    "genre": "剧情类型",
    "language": "zh-CN",
    "version": "1.0",
    "logline": "一句话故事梗概"
  }},
  "source": {{
    "chapter_count": 3,
    "chapter_titles": ["章节标题"]
  }},
  "characters": [
    {{
      "id": "char_001",
      "name": "人物名",
      "role": "protagonist",
      "description": "人物简介"
    }}
  ],
  "locations": [
    {{
      "id": "loc_001",
      "name": "地点名",
      "description": "地点描述"
    }}
  ],
  "scenes": [
    {{
      "id": "scene_001",
      "title": "场景标题",
      "chapter_refs": ["来源章节标题"],
      "location_id": "loc_001",
      "time_of_day": "night",
      "characters": ["char_001"],
      "summary": "场景概要",
      "beats": [
        {{
          "type": "action",
          "content": "动作或舞台说明"
        }},
        {{
          "type": "dialogue",
          "speaker_id": "char_001",
          "content": "对白内容"
        }}
      ]
    }}
  ],
  "notes": ["后续改稿建议"]
}}

小说文本：
{chapter_text}
"""

