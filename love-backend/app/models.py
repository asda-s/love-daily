"""
数据库ORM模型定义模块
定义所有数据库表结构，使用SQLAlchemy ORM
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(32), unique=True, index=True, nullable=False, comment="账号")
    password = Column(String(128), nullable=False, comment="密码(bcrypt加密)")
    nickname = Column(String(32), nullable=False, comment="昵称")
    avatar = Column(String(255), default=None, comment="头像URL")
    invite_code = Column(String(6), unique=True, index=True, nullable=False, comment="邀请码")
    lover_id = Column(Integer, ForeignKey("users.id"), default=None, comment="情侣ID")
    bind_time = Column(DateTime, default=None, comment="绑定情侣时间")
    heart_points = Column(Integer, default=0, comment="心动分")
    level = Column(Integer, default=1, comment="等级")
    created_at = Column(DateTime, default=datetime.now, comment="注册时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    lover = relationship("User", remote_side=[id], backref="lover_of")


class Memory(Base):
    """时光线表"""
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发布人ID")
    title = Column(String(100), nullable=False, comment="标题")
    content = Column(Text, default=None, comment="内容")
    event_time = Column(DateTime, nullable=False, comment="事件发生时间")
    images = Column(Text, default=None, comment="图片URL列表(JSON格式)")
    is_sync = Column(Boolean, default=True, comment="是否同步给情侣")
    created_at = Column(DateTime, default=datetime.now, comment="发布时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    user = relationship("User", backref="memories")


class Anniversary(Base):
    """纪念日表"""
    __tablename__ = "anniversaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    title = Column(String(100), nullable=False, comment="纪念日标题")
    target_date = Column(Date, nullable=False, comment="目标日期")
    is_yearly = Column(Boolean, default=False, comment="是否每年循环")
    remind_days = Column(Integer, default=3, comment="提前提醒天数")
    type = Column(String(20), default="personal", comment="类型: personal-个人, couple-情侣")
    note = Column(Text, default=None, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    user = relationship("User", backref="anniversaries")


class Wish(Base):
    """心愿清单表"""
    __tablename__ = "wishes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    content = Column(String(200), nullable=False, comment="心愿内容")
    status = Column(String(20), default="pending", comment="状态: pending-待完成, completed-已完成")
    complete_time = Column(DateTime, default=None, comment="完成时间")
    note = Column(Text, default=None, comment="备注")
    image = Column(String(255), default=None, comment="打卡图片")
    type = Column(String(20), default="personal", comment="类型: personal-个人, couple-情侣")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    user = relationship("User", backref="wishes")


class Whisper(Base):
    """悄悄话表"""
    __tablename__ = "whispers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发送人ID")
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="接收人ID")
    content = Column(Text, nullable=False, comment="内容")
    send_time = Column(DateTime, default=datetime.now, comment="发送时间")
    is_read = Column(Boolean, default=False, comment="是否已读")
    is_scheduled = Column(Boolean, default=False, comment="是否定时发送")
    scheduled_time = Column(DateTime, default=None, comment="定时发送时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_whispers")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="received_whispers")


class Period(Base):
    """生理期表"""
    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    start_date = Column(Date, nullable=False, comment="开始日期")
    cycle_days = Column(Integer, default=28, comment="周期天数")
    duration_days = Column(Integer, default=5, comment="持续天数")
    note = Column(Text, default=None, comment="备注")
    body_status = Column(Text, default=None, comment="身体状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    user = relationship("User", backref="periods")


class DietPreference(Base):
    """饮食偏好表"""
    __tablename__ = "diet_preferences"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True, comment="用户ID")
    liked_food = Column(Text, default=None, comment="喜欢的食物")
    avoid_food = Column(Text, default=None, comment="忌口的食物")
    allergic_food = Column(Text, default=None, comment="过敏的食物")
    coffee_pref = Column(String(100), default=None, comment="奶茶/咖啡口味偏好")
    delivery_address = Column(Text, default=None, comment="常点外卖地址")
    note = Column(Text, default=None, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    user = relationship("User", backref="diet_preference")


class Todo(Base):
    """待办事项表"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    title = Column(String(100), nullable=False, comment="标题")
    deadline = Column(DateTime, default=None, comment="截止日期")
    remind_time = Column(DateTime, default=None, comment="提醒时间")
    note = Column(Text, default=None, comment="备注")
    status = Column(String(20), default="pending", comment="状态: pending-待完成, completed-已完成")
    type = Column(String(20), default="personal", comment="类型: personal-个人, couple-情侣")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系定义
    user = relationship("User", backref="todos")


class MoodDiary(Base):
    """心情日记表"""
    __tablename__ = "mood_diaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    mood_type = Column(String(20), nullable=False, comment="心情类型: happy/sweet/calm/tired/sad/angry/wronged/surprised")
    mood_intensity = Column(Integer, default=3, comment="心情强度1-5")
    second_mood = Column(String(20), default=None, comment="混合心情第二类型")
    content = Column(Text, nullable=False, comment="日记内容")
    images = Column(Text, default=None, comment="图片JSON数组")
    tags = Column(Text, default=None, comment="标签JSON数组,最多3个")
    is_read = Column(Boolean, default=False, comment="对方是否已读")
    read_time = Column(DateTime, default=None, comment="对方阅读时间")
    publish_status = Column(String(20), default="published", comment="发布状态: draft/published/scheduled")
    scheduled_time = Column(DateTime, default=None, comment="定时发布时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    user = relationship("User", backref="mood_diaries")


class MoodDiaryReaction(Base):
    """日记快速反应表"""
    __tablename__ = "mood_diary_reactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    diary_id = Column(Integer, ForeignKey("mood_diaries.id"), nullable=False, index=True, comment="日记ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    reaction_type = Column(String(20), nullable=False, comment="反应类型: hug/kiss/like/cheer/pat/heart")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    user = relationship("User", backref="diary_reactions")
    diary = relationship("MoodDiary", backref="reactions")

    __table_args__ = (UniqueConstraint('diary_id', 'user_id', name='uq_diary_user_reaction'),)


class MoodDiaryReply(Base):
    """日记回复表（楼中楼）"""
    __tablename__ = "mood_diary_replies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    diary_id = Column(Integer, ForeignKey("mood_diaries.id"), nullable=False, index=True, comment="日记ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    parent_id = Column(Integer, ForeignKey("mood_diary_replies.id"), default=None, comment="父回复ID")
    content = Column(Text, nullable=False, comment="回复内容")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    user = relationship("User", backref="diary_replies")
    diary = relationship("MoodDiary", backref="replies")
    parent = relationship("MoodDiaryReply", remote_side=[id], backref="children")


class MoodDiaryDraft(Base):
    """日记草稿表（每人一条）"""
    __tablename__ = "mood_diary_drafts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, comment="用户ID")
    content = Column(Text, default=None, comment="草稿内容JSON")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    user = relationship("User", backref="diary_draft")


class CheckinProject(Base):
    """打卡项目表"""
    __tablename__ = "checkin_projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    name = Column(String(50), nullable=False, comment="打卡项目名称")
    points = Column(Integer, default=5, comment="单次打卡获得心动分")
    is_joint = Column(Boolean, default=False, comment="是否情侣共同打卡")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    user = relationship("User", backref="checkin_projects")


class CheckinRecord(Base):
    """打卡记录表"""
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("checkin_projects.id"), nullable=False, index=True, comment="打卡项目ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="打卡人ID")
    checkin_date = Column(Date, nullable=False, comment="打卡日期")
    note = Column(Text, default=None, comment="备注")
    image = Column(String(255), default=None, comment="图片")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    project = relationship("CheckinProject", backref="records")
    user = relationship("User", backref="checkin_records")


class Benefit(Base):
    """积分福利表"""
    __tablename__ = "benefits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    name = Column(String(50), nullable=False, comment="福利名称")
    points = Column(Integer, nullable=False, comment="所需心动分")
    rule = Column(Text, default=None, comment="兑换规则")
    is_repeatable = Column(Boolean, default=False, comment="是否可重复兑换")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    user = relationship("User", backref="benefits")


class ExchangeRecord(Base):
    """积分兑换记录表"""
    __tablename__ = "exchange_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    benefit_id = Column(Integer, ForeignKey("benefits.id"), nullable=False, index=True, comment="福利ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="兑换人ID")
    points = Column(Integer, nullable=False, comment="消耗心动分")
    exchange_time = Column(DateTime, default=datetime.now, comment="兑换时间")
    is_fulfilled = Column(Boolean, default=False, comment="是否已兑现")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    benefit = relationship("Benefit", backref="exchange_records")
    user = relationship("User", backref="exchange_records")


class Emotion(Base):
    """情绪树洞表"""
    __tablename__ = "emotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="发布人ID")
    emotion_type = Column(String(20), nullable=False, comment="情绪类型: happy-开心, sad-难过, angry-生气, wronged-委屈, anxious-焦虑")
    content = Column(Text, nullable=False, comment="内容")
    is_sync = Column(Boolean, default=False, comment="是否同步给情侣")
    created_at = Column(DateTime, default=datetime.now, comment="发布时间")

    # 关系定义
    user = relationship("User", backref="emotions")


class Bill(Base):
    """情侣账本表"""
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建人ID")
    amount = Column(Float, nullable=False, comment="开支金额")
    type = Column(String(20), default="other", comment="类型: food-吃饭, travel-旅行, gift-礼物, daily-日常, other-其他")
    pay_time = Column(DateTime, nullable=False, comment="开支时间")
    payer = Column(String(20), nullable=False, comment="支付人: me-我, lover-对方, aa-AA制")
    note = Column(Text, default=None, comment="备注")
    is_aa = Column(Boolean, default=False, comment="是否AA制")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    user = relationship("User", backref="bills")


class Achievement(Base):
    """成就表"""
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    achievement_name = Column(String(50), nullable=False, comment="成就名称")
    description = Column(String(200), nullable=False, comment="成就描述")
    condition = Column(String(200), nullable=False, comment="解锁条件")
    reward_points = Column(Integer, default=0, comment="奖励心动分")
    is_unlocked = Column(Boolean, default=False, comment="是否解锁")
    unlock_time = Column(DateTime, default=None, comment="解锁时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    # 关系定义
    user = relationship("User", backref="achievements")


class LevelBenefit(Base):
    """等级福利表"""
    __tablename__ = "level_benefits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(Integer, unique=True, nullable=False, comment="等级")
    benefit_name = Column(String(50), nullable=False, comment="福利名称")
    description = Column(String(200), nullable=False, comment="福利描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class Notification(Base):
    """通知消息表"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="接收人ID")
    title = Column(String(100), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    type = Column(String(20), default="system", comment="类型: anniversary-纪念日, period-生理期, item-临期, todo-待办, whisper-悄悄话")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    user = relationship("User", backref="notifications")
