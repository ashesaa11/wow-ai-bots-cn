---
name: azerothcore-setup
description: Full automation of AzerothCore WotLK (3.3.5a) server setup on Windows. Use when the user wants to build, compile, configure, or set up an AzerothCore WoW server from scratch. Covers dependency installation (VS2022, MySQL, CMake, OpenSSL, Boost), git clone/fork, CMake configure, VS2022 build, database creation, server launch, and client map data extraction. NOT for in-game content editing or module development.
model: deepseek/deepseek-v4-pro-pg
---

# AzerothCore WotLK Server Setup

Complete Windows setup pipeline for AzerothCore 3.3.5a. Reference `references/config.md` for versions and defaults.

## Workflow

Follow phases in order. Each phase has prerequisites that must be satisfied before proceeding.

### Phase 1: Environment Check & Install

Audit the environment for required dependencies. For each missing dependency:

- **VS2022 C++ workload**: Guide user to VS Installer → Modify → check "Desktop development with C++"
- **MySQL 8.4**: Install via winget (`Oracle.MySQL`), then configure a writable datadir outside Program Files. Use `mysqld --defaults-file=<custom_my.ini> --initialize-insecure` to init. Start with same defaults-file. Create databases `acore_auth`, `acore_characters`, `acore_world` and user `acore`/`acore`.
- **CMake 3.27+**: Install via winget (`Kitware.CMake`). Add to PATH.
- **OpenSSL 3.x**: Download full installer (not Light) from `https://slproweb.com/products/Win32OpenSSL.html`. SourceForge/winget often fails for this. Install to a non-system path to avoid admin prompts.
- **Boost 1.78+**: Download `boost_1_8x_0-msvc-14.3-64.exe` from SourceForge boost-binaries. Browser download recommended — curl frequently fails due to redirects. Install and set BOOST_ROOT env var.

### Phase 2: Source & Build

1. Clone: `git clone --depth 1 --branch master https://github.com/azerothcore/azerothcore-wotlk.git`
2. Fork: use `gh repo fork` if GitHub CLI available, configure `origin`→fork, `upstream`→official
3. CMake configure:
   ```
   cmake -S <source> -B <build> -G "Visual Studio 17 2022" -A x64
         -DTOOLS_BUILD=all -DSCRIPTS=static
         -DBOOST_ROOT=<boost_path> -DOPENSSL_ROOT_DIR=<openssl_path>
   ```
   If git connectivity is poor, add `-DWITHOUT_GIT=1` to skip revision generation.
4. Build: `cmake --build <build> --config RelWithDebInfo --parallel <cores>`
5. Copy DLLs: `libmysql.dll` from MySQL lib, all DLLs from OpenSSL bin, to `<build>/bin/RelWithDebInfo/`
6. Copy configs: `authserver.conf.dist` → `configs/authserver.conf`, `worldserver.conf.dist` → `configs/worldserver.conf` (place in `configs/` subdirectory of bin output). Default DB connection strings match `acore/acore`.

### Phase 3: Database & Launch

1. Ensure MySQL is running: `mysqld --defaults-file=<my.ini>`
2. Start authserver first, wait 8-10s for full init, then worldserver. Both are long-running daemons.
3. First launch auto-creates all tables via SQL updates.

### Phase 4: Account & Client

1. Account creation: use worldserver console command `account create <user> <pass>`, then `account set gmlevel <user> 3 -1`. Do NOT use manual SRP6 SQL — the hash is fragile and often fails.
2. Client `realmlist.wtf` must contain `SET realmlist "127.0.0.1"`.

### Phase 5: Map Data Extraction

Use the batch scripts in `scripts/` (run sequentially, not in parallel):

1. `extract_maps.bat` — DBC + map files (~10-20min, 2-3GB)
2. `extract_vmaps.bat` — Building geometry (~5-10min, ~500MB)
3. `extract_mmaps.bat` — Navigation meshes (~30-60min, ~2GB)

Each script writes to `<build>/bin/RelWithDebInfo/`. After extraction, restart worldserver — the "Failed to find map files" warning should disappear.

## Key Pitfalls

- **OpenSSL Light**: no dev headers. Must use full installer.
- **MySQL in Program Files**: permission denied on data dir init. Use writable location.
- **Boost download**: SourceForge blocks curl. User must download via browser.
- **Account SRP6**: Python-generated hashes are unreliable. Use worldserver console instead.
- **Server launch**: Use PowerShell `Start-Process` or batch `start`. Background bash processes die on session exit.
- **AGENT.md**: Always create and maintain an AGENT.md in the project root tracking progress per phase.

## Resources

- `references/config.md` — version requirements, paths, CMake flags, tool usage
- `scripts/start_servers.bat` — launch authserver + worldserver
- `scripts/extract_maps.bat` — DBC + map extraction
- `scripts/extract_vmaps.bat` — vmap extraction + assembly
- `scripts/extract_mmaps.bat` — mmap generation
