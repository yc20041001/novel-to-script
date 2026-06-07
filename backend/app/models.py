from typing import Literal

from pydantic import BaseModel, Field, field_validator


class NovelChapter(BaseModel):
    title: str = Field(..., min_length=1, description="小说章节标题")
    content: str = Field(..., min_length=1, description="小说章节正文")


class GenerateOptions(BaseModel):
    genre: str | None = Field(default=None, description="剧本类型，例如 悬疑、爱情、奇幻、剧情")
    style: str | None = Field(default=None, description="改编风格，例如 短剧、影视剧、广播剧、舞台剧")
    target_scene_count: int | None = Field(default=None, ge=1, le=50, description="目标场景数量")
    language: str | None = Field(default="zh-CN", description="语言，默认 zh-CN")


class GenerateRequest(BaseModel):
    chapters: list[NovelChapter] = Field(..., min_length=3, description="至少 3 个小说章节")
    options: GenerateOptions | None = Field(default=None, description="可选生成参数")

    @field_validator("chapters")
    @classmethod
    def validate_chapters(cls, chapters: list[NovelChapter]) -> list[NovelChapter]:
        if len(chapters) < 3:
            raise ValueError("请至少输入 3 个章节")
        return chapters


class ScriptMetadata(BaseModel):
    title: str = Field(..., description="剧本标题")
    genre: str = Field(default="剧情", description="剧本类型")
    language: str = Field(default="zh-CN", description="语言代码")
    version: str = Field(default="1.0", description="剧本版本")
    logline: str = Field(default="", description="一句话故事梗概")


class ScriptSource(BaseModel):
    chapter_count: int = Field(..., ge=3, description="输入章节数量")
    chapter_titles: list[str] = Field(..., min_length=3, description="输入章节标题")


class Character(BaseModel):
    id: str = Field(..., description="人物唯一 ID")
    name: str = Field(..., description="人物姓名")
    role: str = Field(default="supporting", description="人物功能")
    description: str = Field(default="", description="人物简介")


class Location(BaseModel):
    id: str = Field(..., description="地点唯一 ID")
    name: str = Field(..., description="地点名称")
    description: str = Field(default="", description="地点描述")


BeatType = Literal["action", "dialogue", "narration", "transition", "sound", "shot"]


class Beat(BaseModel):
    type: BeatType = Field(..., description="剧本节拍类型")
    content: str = Field(..., description="节拍内容")
    speaker_id: str | None = Field(default=None, description="对白说话人物 ID")


class Scene(BaseModel):
    id: str = Field(..., description="场景唯一 ID")
    title: str = Field(..., description="场景标题")
    chapter_refs: list[str] = Field(..., min_length=1, description="来源章节标题")
    location_id: str | None = Field(default=None, description="地点 ID")
    time_of_day: str = Field(default="unspecified", description="场景时间")
    characters: list[str] = Field(default_factory=list, description="登场人物 ID")
    summary: str = Field(default="", description="场景概要")
    beats: list[Beat] = Field(..., min_length=1, description="场景节拍")


class ScriptDocument(BaseModel):
    metadata: ScriptMetadata
    source: ScriptSource
    characters: list[Character] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    scenes: list[Scene] = Field(..., min_length=1)
    notes: list[str] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    script: ScriptDocument
    yaml: str
    used_mock: bool = Field(default=False, description="是否使用演示数据")
    cache_hit: bool = Field(default=False, description="是否命中缓存")
    cache_key: str | None = Field(default=None, description="生成请求缓存键")
    storage: str = Field(default="generated", description="结果来源：generated、redis 或 mysql")


class ValidateYamlRequest(BaseModel):
    yaml: str = Field(..., description="待校验的 YAML 文本")


class ValidateYamlResponse(BaseModel):
    valid: bool = Field(..., description="YAML 是否符合 Schema")
    errors: list[str] = Field(default_factory=list, description="校验错误详情")


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64, description="用户名")
    password: str = Field(..., min_length=1, description="密码")
    captcha_id: str = Field(..., min_length=1, description="验证码 ID")
    captcha_code: str = Field(..., min_length=1, max_length=8, description="验证码")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    display_name: str | None = Field(default=None, max_length=100, description="显示名称")
    captcha_id: str = Field(..., min_length=1, description="验证码 ID")
    captcha_code: str = Field(..., min_length=1, max_length=8, description="验证码")


class CaptchaResponse(BaseModel):
    captcha_id: str = Field(..., description="验证码 ID")
    image: str = Field(..., description="验证码 SVG Data URL")
    expires_in: int = Field(..., description="验证码有效期，单位秒")


class AdminStatsResponse(BaseModel):
    user_count: int = Field(default=0, description="用户总数")
    active_user_count: int = Field(default=0, description="启用用户数")
    project_count: int = Field(default=0, description="项目总数")
    generation_count: int = Field(default=0, description="生成次数")
    script_version_count: int = Field(default=0, description="剧本版本数")
    generated_script_count: int = Field(default=0, description="缓存剧本数")
    mock_generation_count: int = Field(default=0, description="Mock 生成次数")


class AdminUserItem(BaseModel):
    id: int | None = Field(default=None, description="用户 ID")
    username: str = Field(..., description="用户名")
    display_name: str = Field(..., description="显示名称")
    role: str = Field(..., description="角色")
    status: str = Field(default="active", description="用户状态")
    created_at: str | None = Field(default=None, description="创建时间")
    updated_at: str | None = Field(default=None, description="更新时间")


class AdminUsersResponse(BaseModel):
    users: list[AdminUserItem] = Field(default_factory=list, description="用户列表")


class AdminUpdateUserRequest(BaseModel):
    role: str | None = Field(default=None, description="角色：admin 或 author")
    status: str | None = Field(default=None, description="状态：active 或 disabled")


class AdminGenerationRecord(BaseModel):
    id: int | None = Field(default=None, description="记录 ID")
    cache_key: str = Field(..., description="缓存键")
    project_id: int | None = Field(default=None, description="项目 ID")
    project_title: str | None = Field(default=None, description="项目标题")
    chapter_count: int = Field(default=0, description="章节数")
    model_name: str | None = Field(default=None, description="模型名称")
    used_mock: bool = Field(default=False, description="是否使用 Mock")
    yaml_line_count: int = Field(default=0, description="YAML 行数")
    created_at: str | None = Field(default=None, description="创建时间")
    updated_at: str | None = Field(default=None, description="更新时间")


class AdminGenerationRecordsResponse(BaseModel):
    records: list[AdminGenerationRecord] = Field(default_factory=list, description="生成记录")
