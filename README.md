# 魔兽世界 AI 机器人中文版

基于 AzerothCore WotLK (3.3.5a) 的本地服务端，集成 PlayerBots + LLM AI 对话，中文深度定制。

---

## 1. mod-ollama-chat 编码修复

原版模块仅处理 ASCII/UTF-8，WoW zhCN 客户端发送的是 **GBK 编码**。中文字节的 GBK 序列（如「你」=`C4 E3`）不满足 UTF-8 规则，被 `SanitizeUTF8()` 替换为空格，最终在日志和 API 请求中变成 `????`。

### 修改位置

**`src/mod-ollama-chat-utilities.h`** — 添加 `ConvertGBKToUTF8()`：

```cpp
#ifdef _WIN32
#include <windows.h>
inline std::string ConvertGBKToUTF8(const std::string& gbkStr) {
    // 先检测是否包含非 UTF-8 字节（GBK 特征），避免对纯英文做无谓转换
    bool needsConversion = false;
    for (size_t i = 0; i < gbkStr.size(); ) {
        unsigned char c = gbkStr[i];
        if (c <= 0x7F) { i++; continue; }
        if ((c & 0xE0) == 0xC0) { i += 2; continue; }
        if ((c & 0xF0) == 0xE0) { i += 3; continue; }
        if ((c & 0xF8) == 0xF0) { i += 4; continue; }
        needsConversion = true; break;
    }
    if (!needsConversion) return gbkStr;
    // GBK(CP936) → UTF-16 → UTF-8
    int wideLen = MultiByteToWideChar(936, 0, gbkStr.c_str(), -1, nullptr, 0);
    std::wstring wideStr(wideLen, 0);
    MultiByteToWideChar(936, 0, gbkStr.c_str(), -1, &wideStr[0], wideLen);
    int utf8Len = WideCharToMultiByte(CP_UTF8, 0, wideStr.c_str(), -1, nullptr, 0, nullptr, nullptr);
    std::string utf8Str(utf8Len, 0);
    WideCharToMultiByte(CP_UTF8, 0, wideStr.c_str(), -1, &utf8Str[0], utf8Len, nullptr, nullptr);
    if (!utf8Str.empty() && utf8Str.back() == '\0') utf8Str.pop_back();
    return utf8Str;
}
#endif
```

**`src/mod-ollama-chat_handler.cpp`** — 在 `GenerateBotPrompt()` 开头转换，确保 `fmt::format` 不损坏中文字节：

```cpp
std::string GenerateBotPrompt(Player* bot, std::string playerMessage, Player* player) {
    playerMessage = ConvertGBKToUTF8(playerMessage);  // ← 新增
    // ... 后续通过 SafeFormat(fmt::vformat) 构建 prompt
}
```

**`src/mod-ollama-chat_api.cpp`** — 在 `QueryOllamaAPI()` 发送前二次保障：

```cpp
std::string sanitizedPrompt = SanitizeUTF8(ConvertGBKToUTF8(prompt));  // ← 链式转换
```

## 2. Prompt 模板中文化

修改 `conf/mod_ollama_chat.conf`（对应 submodule 中 `conf/mod_ollama_chat.conf.dist`），重写全部 prompt 指令：

| 模板 | 用途 | 旧（英文） | 新（中文） |
|------|------|-----------|-----------|
| `SystemPrompt` | 全局系统指令 | 无 | 「用国服玩家的语气——自然、口语化、可以吐槽、可以开玩笑。适当使用职业简称…」 |
| `ChatPromptTemplate` | 玩家对话回复 | "You're a Wrath-era WoW player... Reply in under 15 words" | 「像国服玩家一样自然回复，可以吐槽、开玩笑、用游戏术语。简短为主…就当你是坐在电脑前的真人」 |
| `RandomChatterPromptTemplate` | 机器人主动闲聊 | 同上英文 | 「用国服玩家语气自然闲聊，可以吐槽、求组、讨论装备」 |
| `EventChatterPromptTemplate` | 事件触发（升级/死亡/任务） | 同上英文 | 「国服玩家语气回应这个事件，可以吐槽或恭喜」 |

关键改动：
- 移除硬性「15字以内」限制 → 「简短为主，需要解释可以多说几句」
- 注入职业简称知识：NQ 奶骑、FQ 防骑、LR 猎人、FS 法师、DZ 盗贼、ZS 战士、MS 牧师、SS 术士、SM 萨满、DK 死骑、XD 小德
- 角色定位从「NPC 旁白」改为「坐在电脑前的真人玩家」

## 3. 中文角色名 & 公会名数据库替换

通过 Python 脚本以随机组字算法生成中文名，替换 `acore_characters` 库的两个表：

```sql
-- 表结构
playerbots_names      (name_id INT, name VARCHAR(12), gender TINYINT)
playerbots_guild_names (name_id INT, name VARCHAR(24))
```

| 字段 | 旧值 | 新值 |
|------|------|------|
| `playerbots_names` 数量 | 100,000（英文） | 3,000（中文，男 1500 + 女 1500） |
| `playerbots_guild_names` 数量 | 400（英文） | 200（中文） |

生成算法：从角色池中随机拼接 2-3 字组合，男名偏「铁/暗/狂/冰/血/龙/魔/战」系，女名偏「月/星/花/雨/雪/薇/灵/梦」系。

示例输出：
```
男: 碎石 黑喙雷 雷霜 狼爪 吟雷 魔影 铁骨魔 煞剑 炎赤 钢刃锤
女: 紫琪 梅雨 铃烟雪 冰萍 霜霜 歌心琳 歌露月 雪蓉 蕾星
公会: 巨龙远征军 蝎子兄弟会 秘法秩序 烈焰城堡 铁炉圣殿 史诗之盾
```

## 4. Ollama → DeepSeek API 代理 (`proxy/server.py`)

手写的 HTTP 代理，对接 mod-ollama-chat 的 `/api/generate` 端点与 DeepSeek `/v1/chat/completions`：

```
worldserver                          proxy:11434                DeepSeek API
mod-ollama-chat ── POST /api/generate ──→ server.py ── POST /v1/chat/completions ──→ api.deepseek.com
     {model, prompt, stream:false}          │                  {model, messages, temperature...}
                                            │                  ← {choices[0].message.content}
         ← {model, response, done:true} ────┘
```

`config.json` 热配置：

```json
{
    "deepseek_api_key": "sk-xxx",
    "deepseek_model": "deepseek-chat",
    "listen_host": "127.0.0.1",
    "listen_port": 11434,
    "max_tokens": 150,
    "temperature": 0.8
}
```

额外支持 `/api/tags` GET 端点模拟 Ollama 模型列表，使模块启动时正常初始化。

## 5. PlayerBots 集成

- 子模块：`liyunfan1223/mod-playerbots`
- 配置：`configs/modules/playerbots.conf`（100 账号 / 1000 角色，自动登录）
- 数据库：`acore_playerbots`（独立库，含 28 张表）

## 项目结构

```
wow-ai-bots-cn/
├── AGENT.md                        # 完整开发日志与踩坑记录
├── README.md
├── .gitignore                      # 排除 build/ mysql_data/ proxy/config.json
├── my.ini                          # MySQL 配置
├── start.bat                       # 一键启动脚本
├── azerothcore-wotlk/              # submodule: ashesaa11/azerothcore-wotlk (liyunfan-playerbot)
│   ├── .gitmodules                 # 子模块注册
│   └── modules/
│       ├── mod-playerbots/         # submodule: liyunfan1223/mod-playerbots
│       └── mod-ollama-chat/        # submodule: ashesaa11/mod-ollama-chat
├── proxy/
│   ├── server.py                   # HTTP 代理（Ollama → DeepSeek）
│   └── config.json                 # API key 与参数（.gitignore 排除）
├── build/                          # CMake 编译输出（.gitignore 排除）
└── World of Warcraft 3.3.5a CN/   # 游戏客户端（.gitignore 排除）
```

## 编译

```bash
cmake -S azerothcore-wotlk -B build -G "Visual Studio 17 2022" -A x64 \
  -DTOOLS_BUILD=all -DSCRIPTS=static \
  -DBOOST_ROOT="D:/local/boost_1_85_0" \
  -DBOOST_INCLUDEDIR="D:/local/boost_1_85_0" \
  -DBOOST_LIBRARYDIR="D:/local/boost_1_85_0/lib64-msvc-14.3" \
  -DOPENSSL_ROOT_DIR="D:/WOW/OpenSSL"

cmake --build build --config RelWithDebInfo --parallel 16
```

## 启动

```bash
# 终端1: MySQL
mysqld --defaults-file=D:\WOW\my.ini

# 终端2: DeepSeek 代理
cd proxy && python server.py

# 终端3: 认证服
D:\WOW\build\bin\RelWithDebInfo\authserver.exe

# 终端4: 世界服（等认证服就绪约10秒）
D:\WOW\build\bin\RelWithDebInfo\worldserver.exe

# worldserver 控制台创建账号
account create admin admin
account set gmlevel admin 3 -1
```

## 依赖

| 组件 | 版本 | 用途 |
|------|------|------|
| Visual Studio 2022 | 17 (MSVC 14.44) | C++ 编译 |
| CMake | 4.3.3 | 构建系统 |
| MySQL | 8.4.9 | 数据库 |
| OpenSSL | 3.5.7 | 加密/网络 |
| Boost | 1.85.0 | C++ 工具库 |
| Python | 3.x | 代理服务 |
| WoW 客户端 | 3.3.5a (zhCN) | 游戏 |

## 相关仓库

| 仓库 | 分支 | 说明 |
|------|------|------|
| [wow-ai-bots-cn](https://github.com/ashesaa11/wow-ai-bots-cn) | master | 项目根 |
| [azerothcore-wotlk](https://github.com/ashesaa11/azerothcore-wotlk) | liyunfan-playerbot | 核心 fork |
| [mod-ollama-chat](https://github.com/ashesaa11/mod-ollama-chat) | main | AI 对话模块 fork |
