# AzerothCore WotLK 服务端

## 项目目标
搭建 AzerothCore 巫妖王之怒 (3.3.5a) 本地服务端，用于单机游戏。

## 当前状态：✅ 已可运行，待验证登录
- 服务端编译完成，authserver + worldserver 正常启动
- 地图数据全部提取完毕 (dbc/maps/vmaps/mmaps)
- 客户端 realmlist 指向 127.0.0.1
- 账号通过 worldserver 控制台创建（**禁止 SQL SRP6 方式，已验证不可靠**）

## 项目路径

| 用途 | 路径 |
|------|------|
| 源码 | `D:\WOW\azerothcore-wotlk` |
| 编译输出 | `D:\WOW\build\bin\RelWithDebInfo` |
| 客户端 | `D:\WOW\World of Warcraft 3.3.5a CN` |
| MySQL 数据 | `D:\WOW\mysql_data` |
| MySQL 配置 | `D:\WOW\my.ini` |
| 批处理脚本 | `D:\WOW\start.bat`, `extract_*.bat` |
| AGENT.md | `D:\WOW\AGENT.md`（本文件，每次推进更新） |

## 环境依赖

| 组件 | 版本 | 路径 | BOOST_ROOT/OPENSSL_ROOT_DIR |
|------|------|------|------|
| VS2022 | 17 (MSVC 14.44) | `D:\Program Files\Microsoft Visual Studio\2022\Community` | — |
| CMake | 4.3.3 | `C:\Program Files\CMake\bin` | — |
| MySQL | 8.4.9 | `C:\Program Files\MySQL\MySQL Server 8.4` | datadir=`D:\WOW\mysql_data` |
| OpenSSL | 3.5.7 | `D:\WOW\OpenSSL` | OPENSSL_ROOT_DIR=`D:\WOW\OpenSSL` |
| Boost | 1.87.0 | `D:\WOW\boost_1_87_0` | BOOST_ROOT=`D:\WOW\boost_1_87_0` |

## 仓库
- origin (Fork): `https://github.com/ashesaa11/azerothcore-wotlk`
- upstream (官方): `https://github.com/azerothcore/azerothcore-wotlk`
- 当前 commit: `f5b21bb`

## 数据库
- 地址: 127.0.0.1:3306
- 用户/密码: acore / acore
- 库: acore_auth / acore_characters / acore_world
- 启动: `mysqld --defaults-file=D:\WOW\my.ini`
- mysql 可执行文件: `C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe`

## 游戏账号
通过 worldserver 控制台 (`AC>`) 创建：
```
account create <用户名> <密码>
account set gmlevel <用户名> 3 -1
```

## 已完成步骤
- [x] VS2022 C++ 桌面开发
- [x] MySQL 8.4 + 数据库 + 用户
- [x] CMake 4.3.3
- [x] OpenSSL 3.5.7 (完整版，非 Light)
- [x] Boost 1.87.0 + BOOST_ROOT
- [x] Git clone + Fork + remote 配置
- [x] CMake Configure + Generate
- [x] VS2022 Build RelWithDebInfo x64 (7个exe)
- [x] DLL 复制 (libmysql + OpenSSL)
- [x] .conf 配置文件 (放于 configs/ 子目录)
- [x] authserver + worldserver 启动
- [x] 数据库自动建表
- [x] 客户端 realmlist.wtf → 127.0.0.1
- [x] DBC + Maps 提取
- [x] vmaps 提取+组装 (12,493 文件)
- [x] mmaps 生成 (3,780 文件)

## 待完成
- [ ] 登录游戏验证（用户手动测试 admin/admin）

## 日常操作

**启动服务端：**
```
双击 D:\WOW\start.bat
```
保留两个命令行窗口。或手动：
```bash
# 窗口1
cd D:\WOW\build\bin\RelWithDebInfo && authserver.exe
# 窗口2（等窗口1加载完毕约10秒后）
cd D:\WOW\build\bin\RelWithDebInfo && worldserver.exe
```

**启动 MySQL：**
```bash
mysqld --defaults-file=D:\WOW\my.ini
```

**重新编译（代码改动后）：**
```bash
cmake --build D:\WOW\build --config RelWithDebInfo --parallel 16
```

**CMake 重新配置（依赖路径因环境变化时）：**
```bash
cmake -S D:\WOW\azerothcore-wotlk -B D:\WOW\build -G "Visual Studio 17 2022" -A x64 -DTOOLS_BUILD=all -DSCRIPTS=static -DBOOST_ROOT="D:\WOW\boost_1_87_0" -DBOOST_INCLUDEDIR="D:\WOW\boost_1_87_0" -DBOOST_LIBRARYDIR="D:\WOW\boost_1_87_0/lib64-msvc-14.3" -DOPENSSL_ROOT_DIR="D:\WOW\OpenSSL"
```

## 踩过的坑 (DO NOT REPEAT)

1. **禁止 SRP6 SQL 创建账号** — Python 计算的 SRP6 hash 格式与 AzerothCore 内部不兼容，永远在 worldserver 控制台用 `account create` 创建
2. **禁止 curl 下载 SourceForge Boost** — SF 重定向系统会返回 HTML 页而非文件，让用户浏览器下载
3. **OpenSSL 必须用完整版** — `ShiningLight.OpenSSL.LTS.Light` (winget) 缺头文件和 lib 文件，从 slproweb.com 下载 Win64OpenSSL 完整安装包
4. **MySQL datadir 不能放 Program Files** — 权限不足，用 `D:\WOW\mysql_data`
5. **cmake 找不到 Boost/OpenSSL 时** — 显式传 `-DBOOST_ROOT` 和 `-DOPENSSL_ROOT_DIR`，不要依赖环境变量
6. **bash 中 `2>&1` 会破坏 MySQL 命令** — Windows bash 误将 `2` 解析为参数，用 PowerShell 或 cmd 执行 MySQL 命令
7. **`start` 命令在 bash 中引号问题** — 启动服务端用 `start_servers.bat` 或让用户手动双击
8. **map_extractor 参数** — 必须 `-i "path" -o "path"`（空格分隔），不能用 `=` 格式

## 可用技能
项目存在用户级技能 `azerothcore-setup`（`~/.qoder/skills/azerothcore-setup/`），包含完整搭建流程、脚本和参考文档。用 `/azerothcore-setup` 可重新执行搭建。
