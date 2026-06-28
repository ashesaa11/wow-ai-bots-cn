# 魔兽世界 AI 机器人中文版

基于 AzerothCore WotLK (3.3.5a) 的本地服务端，集成 AI 聊天机器人，适用于单机游戏。

## 特性

- **PlayerBots**：100 个智能机器人账号，1000 个角色分布全艾泽拉斯，可组队练级打本
- **AI 对话**：通过 DeepSeek 大模型驱动，机器人用中文自然交流，会吐槽、会求组、会讨论装备
- **中文优化**：中文名、中文公会、国服玩家语气，职业简称（NQ/FQ/LR/FS/DZ...）
- **单机友好**：无需联网，本地 MySQL + 本地服务端

## 快速开始

```bash
# 1. 克隆项目（含子模块）
git clone --recursive https://github.com/ashesaa11/wow-ai-bots-cn.git

# 2. 配置 DeepSeek API key
# 编辑 proxy/config.json，填入你的 API key

# 3. 启动 MySQL
mysqld --defaults-file=D:\WOW\my.ini

# 4. 启动代理、authserver、worldserver
cd proxy && python server.py
D:\WOW\build\bin\RelWithDebInfo\authserver.exe
D:\WOW\build\bin\RelWithDebInfo\worldserver.exe

# 5. 登录游戏
# 客户端指向 127.0.0.1，在 worldserver 控制台创建账号
```

## 目录结构

| 路径 | 用途 |
|------|------|
| `azerothcore-wotlk/` | AzerothCore 源码（含 PlayerBots 分支） |
| `proxy/` | Ollama → DeepSeek API 代理 |
| `build/` | 编译输出 |
| `World of Warcraft 3.3.5a CN/` | 游戏客户端 |

## 依赖

- Visual Studio 2022
- CMake 4.3+
- MySQL 8.4
- OpenSSL 3.5+
- Boost 1.85
- Python 3（代理服务）

## 相关仓库

- [azerothcore-wotlk (PlayerBot 分支)](https://github.com/ashesaa11/azerothcore-wotlk)
- [mod-ollama-chat (中文优化)](https://github.com/ashesaa11/mod-ollama-chat)
