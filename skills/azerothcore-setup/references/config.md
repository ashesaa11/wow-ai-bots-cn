# AzerothCore Setup Reference

## Required Versions
- Windows 10+ (x64)
- Visual Studio 2022 Community (C++ Desktop workload, MSVC v143)
- MySQL 8.0+ (8.4 recommended)
- CMake 3.27+
- OpenSSL 3.x (Win64, full with dev headers)
- Boost 1.78+ (precompiled MSVC 14.3 64-bit)
- Git

## Generic Defaults
- DB host: 127.0.0.1:3306
- DB user/pass: acore / acore
- DB names: acore_auth, acore_characters, acore_world
- Game account: created via worldserver console (`account create <user> <pass>`)

## Path Conventions
- Source: `<project>/azerothcore-wotlk`
- Build output: `<project>/build/bin/RelWithDebInfo`
- Client: `<project>/World of Warcraft 3.3.5a CN` (or wherever user places it)
- MySQL data: use a writable location (not Program Files)

## Key CMake Flags
- Generator: Visual Studio 17 2022, platform x64
- -DTOOLS_BUILD=all (includes map extractors)
- -DSCRIPTS=static

## Map Extraction Tools
- map_extractor.exe -i "<client_path>" -o "<build_output>"
- vmap4_extractor.exe -d "<client_path>/Data"
- vmap4_assembler.exe Buildings "<build_output>/vmaps"
- mmaps_generator.exe (run from build output dir)

## Notes
- OpenSSL Light has no dev headers; use full installer from slproweb.com
- Boost from SourceForge may fail with curl; use browser download
- MySQL needs custom datadir outside Program Files (permission issues)
- --depth 1 clone may need WITHOUT_GIT=1 in CMake if git history is unavailable
