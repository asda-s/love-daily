-- 心动日常 - 情侣专属系统 数据库表结构创建脚本
-- 数据库: love_daily
-- 字符集: utf8mb4
-- 引擎: InnoDB

-- 创建数据库
CREATE DATABASE IF NOT EXISTS love_daily DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE love_daily;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(32) NOT NULL UNIQUE COMMENT '账号',
    password VARCHAR(128) NOT NULL COMMENT '密码(bcrypt加密)',
    nickname VARCHAR(32) NOT NULL COMMENT '昵称',
    avatar VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    invite_code VARCHAR(6) NOT NULL UNIQUE COMMENT '邀请码',
    lover_id INT DEFAULT NULL COMMENT '情侣ID',
    heart_points INT DEFAULT 0 COMMENT '心动分',
    level INT DEFAULT 1 COMMENT '等级',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_username (username),
    INDEX idx_invite_code (invite_code),
    INDEX idx_lover_id (lover_id),
    FOREIGN KEY (lover_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 时光线表
CREATE TABLE IF NOT EXISTS memories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '发布人ID',
    title VARCHAR(100) NOT NULL COMMENT '标题',
    content TEXT DEFAULT NULL COMMENT '内容',
    event_time DATETIME NOT NULL COMMENT '事件发生时间',
    images TEXT DEFAULT NULL COMMENT '图片URL列表(JSON格式)',
    is_sync TINYINT(1) DEFAULT 1 COMMENT '是否同步给情侣',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_event_time (event_time),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='时光线表';

-- 纪念日表
CREATE TABLE IF NOT EXISTS anniversaries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '创建人ID',
    title VARCHAR(100) NOT NULL COMMENT '纪念日标题',
    target_date DATE NOT NULL COMMENT '目标日期',
    is_yearly TINYINT(1) DEFAULT 0 COMMENT '是否每年循环',
    remind_days INT DEFAULT 3 COMMENT '提前提醒天数',
    type VARCHAR(20) DEFAULT 'personal' COMMENT '类型: personal-个人, couple-情侣',
    note TEXT DEFAULT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_target_date (target_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='纪念日表';

-- 心愿清单表
CREATE TABLE IF NOT EXISTS wishes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '创建人ID',
    content VARCHAR(200) NOT NULL COMMENT '心愿内容',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending-待完成, completed-已完成',
    complete_time DATETIME DEFAULT NULL COMMENT '完成时间',
    note TEXT DEFAULT NULL COMMENT '备注',
    image VARCHAR(255) DEFAULT NULL COMMENT '打卡图片',
    type VARCHAR(20) DEFAULT 'personal' COMMENT '类型: personal-个人, couple-情侣',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心愿清单表';

-- 悄悄话表
CREATE TABLE IF NOT EXISTS whispers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL COMMENT '发送人ID',
    receiver_id INT NOT NULL COMMENT '接收人ID',
    content TEXT NOT NULL COMMENT '内容',
    send_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读',
    is_scheduled TINYINT(1) DEFAULT 0 COMMENT '是否定时发送',
    scheduled_time DATETIME DEFAULT NULL COMMENT '定时发送时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_sender_id (sender_id),
    INDEX idx_receiver_id (receiver_id),
    INDEX idx_send_time (send_time),
    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='悄悄话表';

-- 生理期表
CREATE TABLE IF NOT EXISTS periods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    start_date DATE NOT NULL COMMENT '开始日期',
    cycle_days INT DEFAULT 28 COMMENT '周期天数',
    duration_days INT DEFAULT 5 COMMENT '持续天数',
    note TEXT DEFAULT NULL COMMENT '备注',
    body_status TEXT DEFAULT NULL COMMENT '身体状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_start_date (start_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生理期表';

-- 饮食偏好表
CREATE TABLE IF NOT EXISTS diet_preferences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL UNIQUE COMMENT '用户ID',
    liked_food TEXT DEFAULT NULL COMMENT '喜欢的食物',
    avoid_food TEXT DEFAULT NULL COMMENT '忌口的食物',
    allergic_food TEXT DEFAULT NULL COMMENT '过敏的食物',
    coffee_pref VARCHAR(100) DEFAULT NULL COMMENT '奶茶/咖啡口味偏好',
    delivery_address TEXT DEFAULT NULL COMMENT '常点外卖地址',
    note TEXT DEFAULT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='饮食偏好表';

-- 待办事项表
CREATE TABLE IF NOT EXISTS todos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '创建人ID',
    title VARCHAR(100) NOT NULL COMMENT '标题',
    deadline DATETIME DEFAULT NULL COMMENT '截止日期',
    remind_time DATETIME DEFAULT NULL COMMENT '提醒时间',
    note TEXT DEFAULT NULL COMMENT '备注',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending-待完成, completed-已完成',
    type VARCHAR(20) DEFAULT 'personal' COMMENT '类型: personal-个人, couple-情侣',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_deadline (deadline),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='待办事项表';

-- 好物收纳表
CREATE TABLE IF NOT EXISTS items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    name VARCHAR(100) NOT NULL COMMENT '物品名称',
    brand VARCHAR(50) DEFAULT NULL COMMENT '品牌',
    model VARCHAR(50) DEFAULT NULL COMMENT '型号',
    spec VARCHAR(50) DEFAULT NULL COMMENT '规格',
    expiry_date DATE DEFAULT NULL COMMENT '保质期',
    purchase_date DATE DEFAULT NULL COMMENT '购买时间',
    open_date DATE DEFAULT NULL COMMENT '开封时间',
    remind_days INT DEFAULT 30 COMMENT '临期提醒天数',
    category VARCHAR(20) DEFAULT 'other' COMMENT '分类: cosmetics-化妆品, skincare-护肤品, clothing-服饰, other-其他',
    note TEXT DEFAULT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_expiry_date (expiry_date),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='好物收纳表';

-- 打卡项目表
CREATE TABLE IF NOT EXISTS checkin_projects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '创建人ID',
    name VARCHAR(50) NOT NULL COMMENT '打卡项目名称',
    points INT DEFAULT 5 COMMENT '单次打卡获得心动分',
    is_joint TINYINT(1) DEFAULT 0 COMMENT '是否情侣共同打卡',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡项目表';

-- 打卡记录表
CREATE TABLE IF NOT EXISTS checkin_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL COMMENT '打卡项目ID',
    user_id INT NOT NULL COMMENT '打卡人ID',
    checkin_date DATE NOT NULL COMMENT '打卡日期',
    note TEXT DEFAULT NULL COMMENT '备注',
    image VARCHAR(255) DEFAULT NULL COMMENT '图片',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_project_id (project_id),
    INDEX idx_user_id (user_id),
    INDEX idx_checkin_date (checkin_date),
    UNIQUE KEY uk_project_user_date (project_id, user_id, checkin_date),
    FOREIGN KEY (project_id) REFERENCES checkin_projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='打卡记录表';

-- 积分福利表
CREATE TABLE IF NOT EXISTS benefits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '创建人ID',
    name VARCHAR(50) NOT NULL COMMENT '福利名称',
    points INT NOT NULL COMMENT '所需心动分',
    rule TEXT DEFAULT NULL COMMENT '兑换规则',
    is_repeatable TINYINT(1) DEFAULT 0 COMMENT '是否可重复兑换',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分福利表';

-- 兑换记录表
CREATE TABLE IF NOT EXISTS exchange_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    benefit_id INT NOT NULL COMMENT '福利ID',
    user_id INT NOT NULL COMMENT '兑换人ID',
    points INT NOT NULL COMMENT '消耗心动分',
    exchange_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '兑换时间',
    is_fulfilled TINYINT(1) DEFAULT 0 COMMENT '是否已兑现',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_benefit_id (benefit_id),
    INDEX idx_user_id (user_id),
    FOREIGN KEY (benefit_id) REFERENCES benefits(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='兑换记录表';

-- 情绪树洞表
CREATE TABLE IF NOT EXISTS emotions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '发布人ID',
    emotion_type VARCHAR(20) NOT NULL COMMENT '情绪类型: happy-开心, sad-难过, angry-生气, wronged-委屈, anxious-焦虑',
    content TEXT NOT NULL COMMENT '内容',
    is_sync TINYINT(1) DEFAULT 0 COMMENT '是否同步给情侣',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情绪树洞表';

-- 情侣账本表
CREATE TABLE IF NOT EXISTS bills (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '创建人ID',
    amount DECIMAL(10,2) NOT NULL COMMENT '开支金额',
    type VARCHAR(20) DEFAULT 'other' COMMENT '类型: food-吃饭, travel-旅行, gift-礼物, daily-日常, other-其他',
    pay_time DATETIME NOT NULL COMMENT '开支时间',
    payer VARCHAR(20) NOT NULL COMMENT '支付人: me-我, lover-对方, aa-AA制',
    note TEXT DEFAULT NULL COMMENT '备注',
    is_aa TINYINT(1) DEFAULT 0 COMMENT '是否AA制',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_pay_time (pay_time),
    INDEX idx_type (type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='情侣账本表';

-- 成就表
CREATE TABLE IF NOT EXISTS achievements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    achievement_name VARCHAR(50) NOT NULL COMMENT '成就名称',
    description VARCHAR(200) NOT NULL COMMENT '成就描述',
    condition VARCHAR(200) NOT NULL COMMENT '解锁条件',
    reward_points INT DEFAULT 0 COMMENT '奖励心动分',
    is_unlocked TINYINT(1) DEFAULT 0 COMMENT '是否解锁',
    unlock_time DATETIME DEFAULT NULL COMMENT '解锁时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_is_unlocked (is_unlocked),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成就表';

-- 等级福利表
CREATE TABLE IF NOT EXISTS level_benefits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    level INT NOT NULL UNIQUE COMMENT '等级',
    benefit_name VARCHAR(50) NOT NULL COMMENT '福利名称',
    description VARCHAR(200) NOT NULL COMMENT '福利描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='等级福利表';

-- 通知消息表
CREATE TABLE IF NOT EXISTS notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '接收人ID',
    title VARCHAR(100) NOT NULL COMMENT '通知标题',
    content TEXT NOT NULL COMMENT '通知内容',
    type VARCHAR(20) DEFAULT 'system' COMMENT '类型: anniversary-纪念日, period-生理期, item-临期, todo-待办, whisper-悄悄话',
    is_read TINYINT(1) DEFAULT 0 COMMENT '是否已读',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知消息表';
