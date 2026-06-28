# 魔兽世界 AI 机器人中文版

基于 AzerothCore WotLK (3.3.5a) 的本地服务端，集成 AI 聊天机器人，适用于单机游戏。

## 修改要点

### 1. mod-ollama-chat 深度定制（submodule: `ashesaa11/mod-ollama-chat`）

| 改动 | 说明 |
|------|------|
| **GBK→UTF-8 编码修复** | 原版仅支持英文编码，中文字符被替换为 `?`。添加 `ConvertGBKToUTF8()` 通过 Win32 `MultiByteToWideChar` 在两层做转换——`GenerateBotPrompt` 格式化前、`QueryOllamaAPI` 发送前 |
| **中文 Prompt 模板** | 重写全部 4 个模板（`ChatPromptTemplate` / `RandomChatterPromptTemplate` / `EventChatterPromptTemplate` / `SystemPrompt`），移除生硬的"15字以内"限制，加入国服职业简称（NQ/FQ/LR/FS/DZ/ZC/MS/SS/DK/XD），指令模型以真人玩家而非 NPC 口吻回复 |
| **中文数据库替换** | `playerbots_names` (100,000→3,000) 和 `playerbots_guild_names` (400→200) 全部替换为中文名，如「铁骨魔」「月影」「巨龙远征军」，通过随机组字算法生成 |

### 2. Ollama → DeepSeek API 代理（`proxy/server.py`）

手写的 HTTP 代理，将 mod-ollama-chat 的 Ollama `/api/generate` 请求转译为 DeepSeek `/v1/chat/completions` 格式，支持：

- 请求/响应格式互转（Ollama JSON ↔ OpenAI Chat JSON）
- `config.json` 热配置（API key / model / temperature 等参数）
- 错误降级（API 超时或 Key 无效时返回空响应，不崩溃 bot 线程）
- 可通过 `/api/tags` 模拟 Ollama 健康检查，使模块正常初始化

### 3. PlayerBot 中文角色系统

- 中文名替换英文名：算法生成 3000 个魔兽风中文名（按性别区分）
- 中文公会替换英文公会：200 个中文公会名
- 数据库表 `playerbots_names` / `playerbots_guild_names` 自动填充

## 架构

```
worldserver (C++)                        proxy (Python)
     │                                       │
     ├─ mod-playerbots ─── PlayerBot 行为     │
     ├─ mod-ollama-chat ─┐                   │
     │     ├─ handler ─── 拦截聊天事件        │
     │     ├─ api ─────── 构造 Prompt ──── HTTP POST /api/generate ──→ Ollama→DeepSeek 代理
     │     └─ httpclient ─ 发送请求          │        │
     │                                       │   DeepSeek API
     └─ 其他 AC 模块                          │   /v1/chat/completions
```

## 快速开始

```bash
# 1. 克隆（含子模块，约 2GB）
git clone --recursive https://github.com/ashesaa11/wow-ai-bots-cn.git

# 2. 配置 API key
# 编辑 proxy/config.json，将 sk-your-api-key-here 替换为 DeepSeek API key

# 3. 启动顺序
mysqld --defaults-file=D:\WOW\my.ini              # 终端1: MySQL
cd proxy && python server.py                      # 终端2: 代理 (port 11434)
D:\WOW\build\bin\RelWithDebInfo\authserver.exe     # 终端3: 认证服
D:\WOW\build\bin\RelWithDebInfo\worldserver.exe    # 终端4: 世界服

# 4. worldserver 控制台创建账号
account create admin admin
account set gmlevel admin 3 -1
```

## 编译

```bash
cmake -S azerothcore-wotlk -B build -G "Visual Studio 17 2022" -A x64 \
  -DTOOLS_BUILD=all -DSCRIPTS=static \
  -DBOOST_ROOT="D:/local/boost_1_85_0" \
  -DOPENSSL_ROOT_DIR="D:/WOW/OpenSSL"

cmake --build build --config RelWithDebInfo --parallel 16
```

## 相关仓库

| 仓库 | 说明 |
|------|------|
| [wow-ai-bots-cn](https://github.com/ashesaa11/wow-ai-bots-cn) | 项目根（部署配置、代理、文档） |
| [azerothcore-wotlk](https://github.com/ashesaa11/azerothcore-wotlk) (分支 `liyunfan-playerbot`) | 核心引擎 + PlayerBot 集成 |
| [mod-ollama-chat](https://github.com/ashesaa11/mod-ollama-chat) | AI 对话模块（编码修复 + 中文定制） |

## 依赖

- Visual Studio 2022 (MSVC 14.44)
- CMake 4.3+
- MySQL 8.4
- OpenSSL 3.5+
- Boost 1.85
- Python 3（代理）
