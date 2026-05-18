# 《心动日常》情侣专属系统 - 分模块任务拆解清单

> 按照需求文档开发优先级排序，每个任务包含具体实现内容

---

## 第一优先级：用户体系与基础框架

### 任务1：后端基础框架搭建
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 1.1 | 创建FastAPI项目，初始化项目结构 | love-backend/app/__init__.py, main.py |
| 1.2 | 配置数据库连接，创建SQLAlchemy引擎 | love-backend/app/database.py |
| 1.3 | 定义环境变量配置，创建.env文件 | love-backend/.env |
| 1.4 | 创建requirements.txt依赖清单 | love-backend/requirements.txt |
| 1.5 | 实现统一接口返回格式和异常处理 | love-backend/app/main.py |
| 1.6 | 配置CORS跨域 | love-backend/app/main.py |

### 任务2：数据库表结构设计与ORM模型
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 2.1 | 设计用户表（users） | love-backend/app/models.py |
| 2.2 | 设计情侣绑定表 | love-backend/app/models.py |
| 2.3 | 设计时光线表（memories） | love-backend/app/models.py |
| 2.4 | 设计纪念日表（anniversaries） | love-backend/app/models.py |
| 2.5 | 设计心愿清单表（wishes） | love-backend/app/models.py |
| 2.6 | 设计悄悄话表（whispers） | love-backend/app/models.py |
| 2.7 | 设计生理期表（periods） | love-backend/app/models.py |
| 2.8 | 设计饮食偏好表（diet_preferences） | love-backend/app/models.py |
| 2.9 | 设计待办事项表（todos） | love-backend/app/models.py |
| 2.10 | 设计好物收纳表（items） | love-backend/app/models.py |
| 2.11 | 设计打卡项目表（checkin_projects） | love-backend/app/models.py |
| 2.12 | 设计打卡记录表（checkin_records） | love-backend/app/models.py |
| 2.13 | 设计积分福利表（benefits） | love-backend/app/models.py |
| 2.14 | 设计积分兑换记录表（exchange_records） | love-backend/app/models.py |
| 2.15 | 设计情绪树洞表（emotions） | love-backend/app/models.py |
| 2.16 | 设计情侣账本表（bills） | love-backend/app/models.py |
| 2.17 | 设计成就表（achievements） | love-backend/app/models.py |
| 2.18 | 设计等级福利表（level_benefits） | love-backend/app/models.py |

### 任务3：JWT鉴权与安全模块
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 3.1 | 实现JWT Token生成与验证 | love-backend/app/security.py |
| 3.2 | 实现bcrypt密码加密 | love-backend/app/security.py |
| 3.3 | 实现用户权限校验中间件 | love-backend/app/security.py |
| 3.4 | 实现情侣数据权限校验 | love-backend/app/security.py |

### 任务4：用户模块接口开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 4.1 | 创建Pydantic入参/出参模型 | love-backend/app/schemas.py |
| 4.2 | 实现用户注册接口（POST /user/register） | love-backend/app/routers/user.py |
| 4.3 | 实现用户登录接口（POST /user/login） | love-backend/app/routers/user.py |
| 4.4 | 实现获取用户信息接口（GET /user/info） | love-backend/app/routers/user.py |
| 4.5 | 实现修改用户信息接口（PUT /user/info） | love-backend/app/routers/user.py |
| 4.6 | 实现情侣绑定接口（POST /user/bind） | love-backend/app/routers/user.py |
| 4.7 | 实现获取情侣信息接口（GET /user/lover） | love-backend/app/routers/user.py |

### 任务5：前端基础框架搭建
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 5.1 | 创建uniapp Vue3项目，初始化目录结构 | love-frontend/ |
| 5.2 | 配置pages.json页面路由和TabBar | love-frontend/pages.json |
| 5.3 | 配置manifest.json项目设置 | love-frontend/manifest.json |
| 5.4 | 实现全局请求封装（Token携带、错误处理、加载提示） | love-frontend/utils/request.js |
| 5.5 | 实现鉴权工具函数（Token存储、登录态判断） | love-frontend/utils/auth.js |
| 5.6 | 实现通用工具函数 | love-frontend/utils/common.js |
| 5.7 | 实现Pinia用户状态管理 | love-frontend/store/user.js |
| 5.8 | 实现Pinia全局状态管理 | love-frontend/store/global.js |
| 5.9 | 实现App.vue根组件（登录态检查） | love-frontend/App.vue |

### 任务6：前端用户模块页面开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 6.1 | 实现登录页面 | love-frontend/pages/user/login.vue |
| 6.2 | 实现注册页面 | love-frontend/pages/user/register.vue |
| 6.3 | 实现情侣绑定弹窗组件 | love-frontend/pages/user/bind.vue |
| 6.4 | 实现个人中心页面（邀请码、情侣信息） | love-frontend/pages/user/profile.vue |
| 6.5 | 实现首页（未绑定展示绑定入口，已绑定展示情侣信息） | love-frontend/pages/index/index.vue |

---

## 第二优先级：时光档案馆与生活管家模块

### 任务7：时光档案馆后端接口开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 7.1 | 实现时光线发布接口（POST /memory/timeline） | love-backend/app/routers/memory.py |
| 7.2 | 实现时光线编辑接口（PUT /memory/timeline/{id}） | love-backend/app/routers/memory.py |
| 7.3 | 实现时光线删除接口（DELETE /memory/timeline/{id}） | love-backend/app/routers/memory.py |
| 7.4 | 实现时光线列表查询接口（GET /memory/timeline） | love-backend/app/routers/memory.py |
| 7.5 | 实现图片上传接口（POST /memory/upload） | love-backend/app/routers/memory.py |
| 7.6 | 实现纪念日CRUD接口 | love-backend/app/routers/memory.py |
| 7.7 | 实现心愿清单CRUD接口 | love-backend/app/routers/memory.py |
| 7.8 | 实现悄悄话发送接口（POST /memory/whisper） | love-backend/app/routers/memory.py |
| 7.9 | 实现悄悄话列表查询接口（GET /memory/whisper） | love-backend/app/routers/memory.py |
| 7.10 | 实现悄悄话已读标记接口（PUT /memory/whisper/{id}/read） | love-backend/app/routers/memory.py |

### 任务8：时光档案馆前端页面开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 8.1 | 实现时光线列表页面（瀑布流卡片布局） | love-frontend/pages/memory/timeline.vue |
| 8.2 | 实现时光线发布页面（多图上传、时间选择） | love-frontend/pages/memory/publish.vue |
| 8.3 | 实现时光线详情页面 | love-frontend/pages/memory/detail.vue |
| 8.4 | 实现纪念日列表页面 | love-frontend/pages/memory/anniversary.vue |
| 8.5 | 实现纪念日新增/编辑页面 | love-frontend/pages/memory/anniversary-edit.vue |
| 8.6 | 实现心愿清单页面（待完成/已完成tab） | love-frontend/pages/memory/wish.vue |
| 8.7 | 实现心愿新增/编辑页面 | love-frontend/pages/memory/wish-edit.vue |
| 8.8 | 实现悄悄话列表页面 | love-frontend/pages/memory/whisper.vue |
| 8.9 | 实现悄悄话发送页面（支持定时发送） | love-frontend/pages/memory/whisper-send.vue |

### 任务9：生活管家后端接口开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 9.1 | 实现生理期记录CRUD接口 | love-backend/app/routers/life.py |
| 9.2 | 实现生理期预测接口（GET /life/period/predict） | love-backend/app/routers/life.py |
| 9.3 | 实现饮食偏好档案CRUD接口 | love-backend/app/routers/life.py |
| 9.4 | 实现待办事项CRUD接口 | love-backend/app/routers/life.py |
| 9.5 | 实现好物收纳CRUD接口 | love-backend/app/routers/life.py |
| 9.6 | 实现好物临期查询接口（GET /life/items/expiring） | love-backend/app/routers/life.py |

### 任务10：生活管家前端页面开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 10.1 | 实现生理期管理页面（日历视图） | love-frontend/pages/life/period.vue |
| 10.2 | 实现生理期记录新增页面 | love-frontend/pages/life/period-edit.vue |
| 10.3 | 实现饮食偏好档案页面 | love-frontend/pages/life/diet.vue |
| 10.4 | 实现待办事项列表页面（待完成/已完成tab） | love-frontend/pages/life/todo.vue |
| 10.5 | 实现待办事项新增/编辑页面 | love-frontend/pages/life/todo-edit.vue |
| 10.6 | 实现好物收纳列表页面（分类筛选） | love-frontend/pages/life/item.vue |
| 10.7 | 实现好物收纳新增/编辑页面 | love-frontend/pages/life/item-edit.vue |

---

## 第三优先级：双人互动空间站模块

### 任务11：双人互动后端接口开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 11.1 | 实现打卡项目CRUD接口 | love-backend/app/routers/interact.py |
| 11.2 | 实现每日打卡接口（POST /interact/checkin） | love-backend/app/routers/interact.py |
| 11.3 | 实现打卡记录查询接口 | love-backend/app/routers/interact.py |
| 11.4 | 实现打卡连续天数计算逻辑 | love-backend/app/routers/interact.py |
| 11.5 | 实现积分福利CRUD接口 | love-backend/app/routers/interact.py |
| 11.6 | 实现积分兑换接口（POST /interact/benefit/exchange） | love-backend/app/routers/interact.py |
| 11.7 | 实现兑换记录查询接口 | love-backend/app/routers/interact.py |
| 11.8 | 实现情绪发布接口（POST /interact/emotion） | love-backend/app/routers/interact.py |
| 11.9 | 实现情绪记录查询接口 | love-backend/app/routers/interact.py |
| 11.10 | 实现情侣账本CRUD接口 | love-backend/app/routers/interact.py |
| 11.11 | 实现账本统计接口（GET /interact/bill/statistics） | love-backend/app/routers/interact.py |

### 任务12：双人互动前端页面开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 12.1 | 实现打卡项目列表页面 | love-frontend/pages/interact/checkin.vue |
| 12.2 | 实现打卡历史记录页面 | love-frontend/pages/interact/checkin-history.vue |
| 12.3 | 实现积分福利列表页面 | love-frontend/pages/interact/benefit.vue |
| 12.4 | 实现积分兑换记录页面 | love-frontend/pages/interact/exchange-history.vue |
| 12.5 | 实现情绪树洞页面 | love-frontend/pages/interact/emotion.vue |
| 12.6 | 实现情绪发布页面 | love-frontend/pages/interact/emotion-publish.vue |
| 12.7 | 实现情侣账本页面（本月统计、分类饼图） | love-frontend/pages/interact/bill.vue |
| 12.8 | 实现账本新增页面 | love-frontend/pages/interact/bill-add.vue |
| 12.9 | 实现月度账单页面 | love-frontend/pages/interact/bill-monthly.vue |

---

## 第四优先级：恋爱养成模块与定时任务

### 任务13：恋爱养成后端接口开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 13.1 | 实现心动分获取接口（POST /love/heart-points/add） | love-backend/app/routers/love.py |
| 13.2 | 实现心动分查询接口（GET /love/heart-points） | love-backend/app/routers/love.py |
| 13.3 | 实现等级信息查询接口（GET /love/level） | love-backend/app/routers/love.py |
| 13.4 | 实现等级自动升级逻辑 | love-backend/app/routers/love.py |
| 13.5 | 实现成就列表查询接口（GET /love/achievements） | love-backend/app/routers/love.py |
| 13.6 | 实现成就自动解锁逻辑 | love-backend/app/routers/love.py |
| 13.7 | 实现等级福利查询接口 | love-backend/app/routers/love.py |

### 任务14：恋爱养成前端页面开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 14.1 | 实现养成主页（等级、心动分、进度条） | love-frontend/pages/love/index.vue |
| 14.2 | 实现成就列表页面（已解锁/未解锁tab） | love-frontend/pages/love/achievement.vue |
| 14.3 | 实现等级福利页面 | love-frontend/pages/love/level-benefit.vue |

### 任务15：定时任务开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 15.1 | 配置APScheduler定时任务框架 | love-backend/app/tasks.py |
| 15.2 | 实现纪念日提醒任务（每日8点） | love-backend/app/tasks.py |
| 15.3 | 实现生理期提醒任务（每日8点，提前3天） | love-backend/app/tasks.py |
| 15.4 | 实现临期物品提醒任务 | love-backend/app/tasks.py |
| 15.5 | 实现待办事项提醒任务 | love-backend/app/tasks.py |
| 15.6 | 实现悄悄话定时发送任务 | love-backend/app/tasks.py |

### 任务16：数据初始化脚本
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 16.1 | 创建数据库表结构SQL脚本 | love-backend/init_db.sql |
| 16.2 | 创建默认数据初始化脚本（等级福利、成就定义） | love-backend/init_data.sql |

---

## 第五优先级：优化、部署与文档

### 任务17：前端兼容性适配与优化
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 17.1 | 微信小程序平台适配（域名校验、本地存储） | 多文件 |
| 17.2 | H5端适配与测试 | 多文件 |
| 17.3 | APP端适配与测试 | 多文件 |
| 17.4 | 图片压缩与懒加载优化 | 多文件 |
| 17.5 | 首屏加载性能优化 | 多文件 |

### 任务18：后端优化
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 18.1 | 数据库索引优化 | love-backend/app/models.py |
| 18.2 | 接口响应性能优化 | 多文件 |
| 18.3 | 异常处理完善 | 多文件 |
| 18.4 | 接口文档完善 | 多文件 |

### 任务19：部署配置
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 19.1 | 创建Dockerfile | love-backend/Dockerfile |
| 19.2 | 创建docker-compose.yml | love-backend/docker-compose.yml |
| 19.3 | 编写本地开发环境搭建文档 | love-backend/README.md |

### 任务20：全局通用组件开发
| 子任务 | 内容 | 输出文件 |
|--------|------|----------|
| 20.1 | 开发空状态组件 | love-frontend/components/Empty.vue |
| 20.2 | 开发加载组件 | love-frontend/components/Loading.vue |
| 20.3 | 开发卡片组件 | love-frontend/components/Card.vue |
| 20.4 | 开发确认弹窗组件 | love-frontend/components/ConfirmDialog.vue |
| 20.5 | 开发图片上传组件 | love-frontend/components/ImageUpload.vue |

---

## 任务依赖关系

```
任务1（后端基础框架）→ 任务2（数据库设计）→ 任务3（鉴权模块）→ 任务4（用户接口）
任务5（前端基础框架）→ 任务6（用户页面）
任务4 + 任务6 → 任务7-8（时光档案馆）→ 任务9-10（生活管家）→ 任务11-12（双人互动）→ 任务13-14（恋爱养成）
任务7-14 → 任务15（定时任务）
任务1-14 → 任务17-18（优化）→ 任务19（部署）→ 任务20（通用组件）
```

---

## 预计工作量分布

| 优先级 | 模块 | 任务数 | 工作量占比 |
|--------|------|--------|------------|
| 第一优先级 | 用户体系与基础框架 | 6个任务，35个子任务 | 35% |
| 第二优先级 | 时光档案馆与生活管家 | 4个任务，33个子任务 | 30% |
| 第三优先级 | 双人互动空间站 | 2个任务，20个子任务 | 20% |
| 第四优先级 | 恋爱养成与定时任务 | 4个任务，18个子任务 | 10% |
| 第五优先级 | 优化、部署与文档 | 4个任务，17个子任务 | 5% |
