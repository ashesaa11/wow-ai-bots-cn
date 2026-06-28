# 魔兽世界 AI 机器人中文版(更适合中国宝宝的机器人单机魔兽)

AzerothCore WotLK (3.3.5a) 本地服务端，集成 PlayerBots + LLM AI 对话，中文深度定制。

## 引用声明

本项目基于以下开源仓库构建，感谢原作者：

| 上游仓库 | 用途 | 本仓库对应 |
|------|------|------|
| [liyunfan1223/azerothcore-wotlk](https://github.com/liyunfan1223/azerothcore-wotlk) | AC 核心（PlayerBot 分支） | [fork](https://github.com/ashesaa11/azerothcore-wotlk) |
| [liyunfan1223/mod-playerbots](https://github.com/liyunfan1223/mod-playerbots) | 机器人行为系统 | 直接引用，未修改 |
| [DustinHendrickson/mod-ollama-chat](https://github.com/DustinHendrickson/mod-ollama-chat) | LLM AI 对话模块 | [fork](https://github.com/ashesaa11/mod-ollama-chat)（中文定制） |

## 游戏客户端

下载 WoW 3.3.5a 简体中文客户端（约 16GB）：

👉 [https://www.xspio.com/魔兽世界官方客户端下载/](https://www.xspio.com/%E9%AD%94%E5%85%BD%E4%B8%96%E7%95%8C%E5%AE%98%E6%96%B9%E5%AE%A2%E6%88%B7%E7%AB%AF%E4%B8%8B%E8%BD%BD/)

下载后解压到项目根目录，确保路径为 `World of Warcraft 3.3.5a CN/`。

---

## 做了什么

- **GBK→UTF-8 编码修复**：解决 zhCN 客户端中文乱码，使 LLM 正确接收中文输入
- **中文 Prompt 模板**：重写全部对话模板，国服玩家语气，支持职业简称，移除「15字以内」硬限制
- **中文角色名 & 公会名**：替换英文名数据库，算法生成 3000 个魔兽风中文名 + 200 个中文公会名
- **自写 API 代理**：`proxy/server.py` 将 Ollama 格式请求转译为 DeepSeek `/v1/chat/completions`

## 一键 AI 安装

项目内置 `skills/azerothcore-setup/` skill，可用任意 AI Agent 工具（Qoder CLI、Claude Code、Cursor 等）一键完成环境安装和编译。将 skill 目录导入你的 Agent 工具后，只需输入：

```
帮我搭建 AzerothCore 魔兽世界服务端
```

Agent 会自动安装 VS2022、MySQL、CMake、OpenSSL、Boost，克隆代码，配置 CMake，编译，并提取地图数据。详见 `skills/azerothcore-setup/SKILL.md`。

## 环境依赖

| 组件 | 版本 | 说明 |
|------|------|------|
| Visual Studio 2022 | 17 (MSVC 14.44) | C++ 桌面开发工作负载 |
| CMake | 4.3+ | 需在 PATH 中 |
| MySQL | 8.4 | 需在 PATH 中 |
| OpenSSL | 3.5+ | [Win64OpenSSL 完整版](https://slproweb.com/products/Win32OpenSSL.html) |
| Boost | 1.85 | 预编译版本 |
| Python | 3.x | 运行代理脚本 |
| Git | 2.x | 含 submodule 支持 |

## 本地搭建教程

### 1. 克隆项目

```bash
git clone --recursive https://github.com/ashesaa11/wow-ai-bots-cn.git
cd wow-ai-bots-cn
```

### 2. 安装依赖

- **VS2022**：安装时勾选「使用 C++ 的桌面开发」
- **CMake**：从 [cmake.org](https://cmake.org/download/) 下载安装
- **MySQL 8.4**：从 [mysql.com](https://dev.mysql.com/downloads/mysql/) 下载，安装后确保 `mysql.exe` 和 `mysqld.exe` 在 PATH
- **OpenSSL**：从 [slproweb.com](https://slproweb.com/products/Win32OpenSSL.html) 下载 **Win64OpenSSL（完整版，非 Light）**，安装到 `D:\WOW\OpenSSL`
- **Boost 1.85**：下载预编译 [boost_1_85_0-msvc-14.3-64.exe](https://sourceforge.net/projects/boost/files/boost-binaries/)，安装到 `D:\local\boost_1_85_0`

### 3. 初始化 MySQL

```bash
# 初始化数据目录
mysqld --initialize-insecure --datadir=D:\WOW\mysql_data

# 创建 acore 用户和数据库
mysqld --defaults-file=D:\WOW\my.ini
mysql -u root < create_acore_user.sql   # 如无此文件，手动执行下方 SQL
```

手动创建用户（在 mysql 控制台执行）：
```sql
CREATE USER 'acore'@'127.0.0.1' IDENTIFIED BY 'acore';
GRANT ALL PRIVILEGES ON *.* TO 'acore'@'127.0.0.1' WITH GRANT OPTION;
CREATE DATABASE acore_auth;
CREATE DATABASE acore_characters;
CREATE DATABASE acore_world;
CREATE DATABASE acore_playerbots;
```

### 4. 导入数据库

需要 AzerothCore 官方的 SQL 基础数据（由于授权原因不包含在本仓库）：

```bash
# 下载 TDB_full_world_335.24071_2025_06_14.7z 并解压
mysql -u root acore_world < TDB_full_world_335.24071_2025_06_14.sql
```

### 5. CMake 配置 & 编译

```bash
cmake -S azerothcore-wotlk -B build -G "Visual Studio 17 2022" -A x64 \
  -DTOOLS_BUILD=all -DSCRIPTS=static \
  -DBOOST_ROOT="D:/local/boost_1_85_0" \
  -DBOOST_INCLUDEDIR="D:/local/boost_1_85_0" \
  -DBOOST_LIBRARYDIR="D:/local/boost_1_85_0/lib64-msvc-14.3" \
  -DOPENSSL_ROOT_DIR="D:/WOW/OpenSSL"

cmake --build build --config RelWithDebInfo --parallel 16
```

编译完成后，输出在 `build/bin/RelWithDebInfo/`：
- `authserver.exe`
- `worldserver.exe`
- `map_extractor.exe` / `vmap4_extractor.exe` 等工具

### 6. 提取地图数据

需要将 WoW 3.3.5a zhCN 客户端（`World of Warcraft 3.3.5a CN/`）放在项目根目录，然后：

```bash
# DBC & Maps
build\bin\RelWithDebInfo\map_extractor.exe -i "World of Warcraft 3.3.5a CN" -o "build\bin\RelWithDebInfo"

# VMaps
build\bin\RelWithDebInfo\vmap4_extractor.exe
build\bin\RelWithDebInfo\vmap4_assembler.exe

# MMaps
build\bin\RelWithDebInfo\mmaps_generator.exe
```

### 7. 配置 DeepSeek API Key

编辑 `proxy/config.json`，填入你的 DeepSeek API key：

```json
{
    "deepseek_api_key": "sk-你的key",
    "deepseek_model": "deepseek-chat",
    "listen_host": "127.0.0.1",
    "listen_port": 11434
}
```

### 8. 启动服务端

**顺序启动 4 个进程**，每个一个终端窗口：

```bash
# 终端1: MySQL
mysqld --defaults-file=D:\WOW\my.ini

# 终端2: DeepSeek 代理
cd proxy
python server.py
# 输出: Ollama→DeepSeek proxy running on http://127.0.0.1:11434

# 终端3: 认证服
build\bin\RelWithDebInfo\authserver.exe

# 终端4: 世界服（等认证服就绪约10秒）
build\bin\RelWithDebInfo\worldserver.exe
```

世界服首次启动会自动建表、更新数据库、初始化 1000 个中文名机器人。看到 `AC>` 提示符即就绪。

### 9. 登录游戏

1. 确保 WoW 3.3.5a 客户端 `realmlist.wtf` 内容为 `set realmlist 127.0.0.1`
2. 在 worldserver 控制台创建账号：
```
account create admin admin
account set gmlevel admin 3 -1
```
3. 启动 Wow.exe，用 `admin` / `admin` 登录

### 10. 测试 AI 聊天

游戏内说话（`/s`）或队伍聊天（`/p`），附近机器人会自动用中文回复。可通过以下命令管理机器人：

```
.bot add warrior    # 添加战士机器人到队伍
.bot remove         # 移除所有机器人
.bot help           # 查看全部命令
```

修改对话参数参考 `build/bin/RelWithDebInfo/configs/modules/mod_ollama_chat.conf`。

## 项目结构

```
wow-ai-bots-cn/
├── AGENT.md                         # 开发日志
├── .gitignore                       # 排除 build/ mysql_data/ 客户端/ proxy/config.json
├── azerothcore-wotlk/               # submodule: AzerothCore + PlayerBots (liyunfan-playerbot)
│   └── modules/
│       ├── mod-playerbots/          # submodule: 机器人行为系统
│       └── mod-ollama-chat/         # submodule: LLM 对话（编码修复 + 中文定制）
├── proxy/
│   ├── server.py                    # Ollama → DeepSeek HTTP 代理
│   └── config.json                  # API key 配置（gitignore）
├── build/                           # CMake 编译输出
└── World of Warcraft 3.3.5a CN/    # 游戏客户端（自行准备）
```

## 相关仓库

| 仓库 | 说明 |
|------|------|
| [wow-ai-bots-cn](https://github.com/ashesaa11/wow-ai-bots-cn) | 项目根 |
| [azerothcore-wotlk](https://github.com/ashesaa11/azerothcore-wotlk) | 核心引擎 fork |
| [mod-ollama-chat](https://github.com/ashesaa11/mod-ollama-chat) | AI 对话模块 fork |
