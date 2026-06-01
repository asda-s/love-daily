"""
Pydantic数据模型定义模块
定义所有接口的入参、出参校验模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date


# ==================== 用户模块 ====================

class UserRegister(BaseModel):
    """用户注册入参"""
    username: str = Field(..., min_length=3, max_length=32, description="账号")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    nickname: str = Field(..., min_length=2, max_length=32, description="昵称")


class UserLogin(BaseModel):
    """用户登录入参"""
    username: str = Field(..., description="账号")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户信息修改入参"""
    nickname: Optional[str] = Field(None, min_length=2, max_length=32, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    old_password: Optional[str] = Field(None, description="原密码")
    new_password: Optional[str] = Field(None, min_length=6, max_length=32, description="新密码")


class BindLover(BaseModel):
    """情侣绑定入参"""
    invite_code: str = Field(..., min_length=6, max_length=6, description="邀请码")


class UserResponse(BaseModel):
    """用户信息出参"""
    id: int
    username: str
    nickname: str
    avatar: Optional[str]
    invite_code: str
    lover_id: Optional[int]
    heart_points: int
    level: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class LoverResponse(BaseModel):
    """情侣信息出参"""
    id: int
    nickname: str
    avatar: Optional[str]
    heart_points: int
    level: int

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token响应出参"""
    token: str
    user_id: int
    nickname: str


# ==================== 时光档案馆模块 ====================

class MemoryCreate(BaseModel):
    """时光线创建入参"""
    title: str = Field(..., min_length=1, max_length=100, description="标题")
    content: Optional[str] = Field(None, description="内容")
    event_time: datetime = Field(..., description="事件发生时间")
    images: Optional[str] = Field(None, description="图片URL列表(JSON格式)")
    is_sync: bool = Field(True, description="是否同步给情侣")


class MemoryUpdate(BaseModel):
    """时光线更新入参"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="标题")
    content: Optional[str] = Field(None, description="内容")
    event_time: Optional[datetime] = Field(None, description="事件发生时间")
    images: Optional[str] = Field(None, description="图片URL列表(JSON格式)")
    is_sync: Optional[bool] = Field(None, description="是否同步给情侣")


class AnniversaryCreate(BaseModel):
    """纪念日创建入参"""
    title: str = Field(..., min_length=1, max_length=100, description="纪念日标题")
    target_date: date = Field(..., description="目标日期")
    is_yearly: bool = Field(False, description="是否每年循环")
    remind_days: int = Field(3, ge=1, le=30, description="提前提醒天数")
    type: Literal["personal", "couple"] = Field("personal", description="类型: personal-个人, couple-情侣")
    note: Optional[str] = Field(None, description="备注")


class AnniversaryUpdate(BaseModel):
    """纪念日更新入参"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="纪念日标题")
    target_date: Optional[date] = Field(None, description="目标日期")
    is_yearly: Optional[bool] = Field(None, description="是否每年循环")
    remind_days: Optional[int] = Field(None, ge=1, le=30, description="提前提醒天数")
    type: Optional[str] = Field(None, description="类型")
    note: Optional[str] = Field(None, description="备注")


class WishCreate(BaseModel):
    """心愿创建入参"""
    content: str = Field(..., min_length=1, max_length=200, description="心愿内容")
    type: Literal["personal", "couple"] = Field("personal", description="类型: personal-个人, couple-情侣")
    note: Optional[str] = Field(None, description="备注")


class WishComplete(BaseModel):
    """心愿完成入参"""
    complete_time: datetime = Field(..., description="完成时间")
    image: Optional[str] = Field(None, description="打卡图片")


class WhisperCreate(BaseModel):
    """悄悄话创建入参"""
    content: str = Field(..., min_length=1, max_length=2000, description="内容")
    is_scheduled: bool = Field(False, description="是否定时发送")
    scheduled_time: Optional[datetime] = Field(None, description="定时发送时间")


# ==================== 生活管家模块 ====================

class PeriodCreate(BaseModel):
    """生理期记录创建入参"""
    start_date: date = Field(..., description="开始日期")
    cycle_days: int = Field(28, ge=20, le=45, description="周期天数")
    duration_days: int = Field(5, ge=2, le=10, description="持续天数")
    note: Optional[str] = Field(None, description="备注")
    body_status: Optional[str] = Field(None, description="身体状态")


class PeriodUpdate(BaseModel):
    """生理期记录更新入参"""
    start_date: Optional[date] = Field(None, description="开始日期")
    cycle_days: Optional[int] = Field(None, ge=20, le=45, description="周期天数")
    duration_days: Optional[int] = Field(None, ge=2, le=10, description="持续天数")
    note: Optional[str] = Field(None, description="备注")
    body_status: Optional[str] = Field(None, description="身体状态")


class DietPreferenceCreate(BaseModel):
    """饮食偏好创建入参"""
    liked_food: Optional[str] = Field(None, description="喜欢的食物")
    avoid_food: Optional[str] = Field(None, description="忌口的食物")
    allergic_food: Optional[str] = Field(None, description="过敏的食物")
    coffee_pref: Optional[str] = Field(None, description="奶茶/咖啡口味偏好")
    delivery_address: Optional[str] = Field(None, description="常点外卖地址")
    note: Optional[str] = Field(None, description="备注")


class TodoCreate(BaseModel):
    """待办事项创建入参"""
    title: str = Field(..., min_length=1, max_length=100, description="标题")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    remind_time: Optional[datetime] = Field(None, description="提醒时间")
    note: Optional[str] = Field(None, description="备注")
    type: Literal["personal", "couple"] = Field("personal", description="类型: personal-个人, couple-情侣")


class TodoUpdate(BaseModel):
    """待办事项更新入参"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="标题")
    deadline: Optional[datetime] = Field(None, description="截止日期")
    remind_time: Optional[datetime] = Field(None, description="提醒时间")
    note: Optional[str] = Field(None, description="备注")
    status: Optional[Literal["pending", "completed"]] = Field(None, description="状态")


class MoodDiaryCreate(BaseModel):
    """心情日记创建入参"""
    mood_type: Literal["happy", "sweet", "calm", "tired", "sad", "angry", "wronged", "surprised"] = Field(..., description="心情类型")
    mood_intensity: int = Field(3, ge=1, le=5, description="心情强度1-5")
    second_mood: Optional[Literal["happy", "sweet", "calm", "tired", "sad", "angry", "wronged", "surprised"]] = Field(None, description="混合心情第二类型")
    content: str = Field(..., min_length=1, max_length=5000, description="日记内容")
    images: Optional[List[str]] = Field(None, max_length=9, description="图片URL列表，最多9张")
    tags: Optional[List[str]] = Field(None, max_length=3, description="标签列表，最多3个")
    diary_date: date = Field(..., description="日记日期（记录哪一天的心情）")
    publish_status: Literal["draft", "published", "scheduled"] = Field("published", description="发布状态")
    scheduled_time: Optional[datetime] = Field(None, description="定时发布时间")


class MoodDiaryUpdate(BaseModel):
    """心情日记更新入参"""
    mood_type: Optional[Literal["happy", "sweet", "calm", "tired", "sad", "angry", "wronged", "surprised"]] = Field(None, description="心情类型")
    mood_intensity: Optional[int] = Field(None, ge=1, le=5, description="心情强度1-5")
    second_mood: Optional[Literal["happy", "sweet", "calm", "tired", "sad", "angry", "wronged", "surprised"]] = Field(None, description="混合心情第二类型")
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="日记内容")
    images: Optional[List[str]] = Field(None, max_length=9, description="图片URL列表，最多9张")
    tags: Optional[List[str]] = Field(None, max_length=3, description="标签列表，最多3个")
    diary_date: Optional[date] = Field(None, description="日记日期")


class MoodDiaryReactionCreate(BaseModel):
    """日记快速反应入参"""
    reaction_type: Literal["hug", "kiss", "like", "cheer", "pat", "heart"] = Field(..., description="反应类型")


class MoodDiaryReplyCreate(BaseModel):
    """日记回复入参"""
    content: str = Field(..., min_length=1, max_length=1000, description="回复内容")
    parent_id: Optional[int] = Field(None, description="父回复ID，楼中楼")


class MoodDiaryDraftSave(BaseModel):
    """日记草稿保存入参"""
    content: str = Field(..., description="草稿内容JSON")


# ==================== 双人互动模块 ====================

class CheckinProjectCreate(BaseModel):
    """打卡项目创建入参"""
    name: str = Field(..., min_length=1, max_length=50, description="打卡项目名称")
    points: int = Field(5, ge=1, le=100, description="单次打卡获得心动分")
    is_joint: bool = Field(False, description="是否情侣共同打卡")


class CheckinCreate(BaseModel):
    """打卡记录创建入参"""
    project_id: int = Field(..., description="打卡项目ID")
    note: Optional[str] = Field(None, description="备注")
    image: Optional[str] = Field(None, description="图片")


class BenefitCreate(BaseModel):
    """积分福利创建入参"""
    name: str = Field(..., min_length=1, max_length=50, description="福利名称")
    points: int = Field(..., ge=1, description="所需心动分")
    rule: Optional[str] = Field(None, description="兑换规则")
    is_repeatable: bool = Field(False, description="是否可重复兑换")


class BenefitUpdate(BaseModel):
    """积分福利更新入参"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="福利名称")
    points: Optional[int] = Field(None, ge=1, description="所需心动分")
    rule: Optional[str] = Field(None, description="兑换规则")
    is_repeatable: Optional[bool] = Field(None, description="是否可重复兑换")


class EmotionCreate(BaseModel):
    """情绪发布入参"""
    emotion_type: Literal["happy", "sad", "angry", "wronged", "anxious"] = Field(..., description="情绪类型")
    content: str = Field(..., min_length=1, max_length=2000, description="内容")
    is_sync: bool = Field(False, description="是否同步给情侣")


class BillCreate(BaseModel):
    """情侣账本创建入参"""
    amount: float = Field(..., gt=0, description="开支金额")
    type: Literal["food", "travel", "gift", "daily", "other"] = Field("other", description="类型")
    pay_time: datetime = Field(..., description="开支时间")
    payer: Literal["me", "lover", "aa"] = Field(..., description="支付人")
    note: Optional[str] = Field(None, description="备注")
    is_aa: bool = Field(False, description="是否AA制")


class BillUpdate(BaseModel):
    """情侣账本更新入参"""
    amount: Optional[float] = Field(None, gt=0, description="开支金额")
    type: Optional[Literal["food", "travel", "gift", "daily", "other"]] = Field(None, description="类型")
    pay_time: Optional[datetime] = Field(None, description="开支时间")
    payer: Optional[Literal["me", "lover", "aa"]] = Field(None, description="支付人")
    note: Optional[str] = Field(None, description="备注")
    is_aa: Optional[bool] = Field(None, description="是否AA制")


# ==================== 恋爱养成模块 ====================

class HeartPointAdd(BaseModel):
    """心动分增加入参"""
    points: int = Field(..., ge=1, description="心动分数量")
    reason: str = Field(..., description="获取原因")
