from app.models import (
    Beat,
    Character,
    Location,
    Scene,
    ScriptDocument,
    ScriptMetadata,
    ScriptSource,
)


def build_mock_script(chapter_titles: list[str]) -> ScriptDocument:
    return ScriptDocument(
        metadata=ScriptMetadata(
            title="雨夜来信",
            genre="悬疑",
            language="zh-CN",
            version="1.0",
            logline="一名编辑在雨夜收到一份能预写现实的神秘手稿。",
        ),
        source=ScriptSource(
            chapter_count=len(chapter_titles),
            chapter_titles=chapter_titles,
        ),
        characters=[
            Character(
                id="char_001",
                name="林晚",
                role="protagonist",
                description="年轻编辑，理性谨慎，却被神秘手稿卷入异常事件。",
            )
        ],
        locations=[
            Location(
                id="loc_001",
                name="旧书店",
                description="位于巷尾的老书店，木楼梯通向昏暗二楼。",
            )
        ],
        scenes=[
            Scene(
                id="scene_001",
                title="雨夜入店",
                chapter_refs=[chapter_titles[0]],
                location_id="loc_001",
                time_of_day="night",
                characters=["char_001"],
                summary="林晚在旧书店发现一份无名手稿。",
                beats=[
                    Beat(type="action", content="雨声压过街道，林晚抱着退稿推开旧书店的门。"),
                    Beat(type="sound", content="门口铜铃轻响。"),
                    Beat(type="action", content="她注意到柜台上的牛皮纸袋，迟疑后将它打开。"),
                ],
            ),
            Scene(
                id="scene_002",
                title="写着她名字的第一页",
                chapter_refs=[chapter_titles[1]],
                location_id="loc_001",
                time_of_day="night",
                characters=["char_001"],
                summary="手稿内容开始与现实重合。",
                beats=[
                    Beat(type="action", content="林晚翻开手稿，第一页赫然写着她的名字。"),
                    Beat(type="dialogue", speaker_id="char_001", content="这是谁写的？"),
                    Beat(type="sound", content="电话里传来断断续续的电流声。"),
                ],
            ),
            Scene(
                id="scene_003",
                title="打字机的警告",
                chapter_refs=[chapter_titles[2]],
                location_id="loc_001",
                time_of_day="night",
                characters=["char_001"],
                summary="林晚在二楼看到自动打字的打字机。",
                beats=[
                    Beat(type="action", content="楼上传来脚步声，林晚握紧手机走上木楼梯。"),
                    Beat(type="action", content="二楼空无一人，老式打字机却自行敲动。"),
                    Beat(type="shot", content="特写：白纸上出现一行字。"),
                    Beat(type="narration", content="不要相信结局。"),
                ],
            ),
        ],
        notes=["当前为演示剧本。配置 DeepSeek API Key 后可根据输入小说实时生成。"],
    )

