# Phase 27 SHARE Strict Baseline Functional Domain Audit

Date: 2026-06-01

## Decision

- Status: `passed_strict_share_wave1_functional_available`
- Recommended action: `promote_share_wave1_to_strict_primary_after_merge`
- Evidence path: `/mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta`
- Evidence variables: `adl;iadl`

## Interpretation

SHARE can be upgraded from the current wave-6 bridge-only functional-domain construction to a strict wave-1 functional-domain construction, because a local SHARE wave-1 Stata file contains both `adl` and `iadl` with explicit ADL/IADL limitation labels and a mergeable `mergeid` key.

Implementation rule: merge `adl` and `iadl` from the evidence file into the cleaned SHARE rows by `mergeid`, restrict the strict SHARE analysis selection to wave 1, and use `adl + iadl` as the SHARE functional score source.

## Top Candidate Evidence

| Source layer | Wave | Variable | Category | Strict | Nonmissing | Label | Source |
|---|---|---|---|---:|---:|---|---|
| raw_share_release | 1 | `adl` | strict_adl_iadl | 1 | 30270 | Number of limitations with activities of daily living (adl) | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_health.dta |
| raw_share_release | 1 | `adl2` | strict_adl_iadl | 1 | 30270 | 1+ adl limitations | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_health.dta |
| raw_share_release | 1 | `iadl` | strict_adl_iadl | 1 | 30270 | Limitations with instrumental activities of daily living (iadl) | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_health.dta |
| raw_share_release | 1 | `iadl2` | strict_adl_iadl | 1 | 30270 | 1+ iadl limitations | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_health.dta |
| raw_share_release | 1 | `adl` | strict_adl_iadl | 1 | 152080 | Limitations with activities of daily living | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_imputations.dta |
| raw_share_release | 1 | `adl_f` | strict_adl_iadl | 1 | 152080 | Limitations with activities of daily living - Flag | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_imputations.dta |
| raw_share_release | 1 | `iadl` | strict_adl_iadl | 1 | 152080 | Limitations with instrumental activities of daily living | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_imputations.dta |
| raw_share_release | 1 | `iadl_f` | strict_adl_iadl | 1 | 152080 | Limitations with instrumental activities of daily living - Flag | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Raw_data/Wave 1 Release 9.0.0/sharew1_rel9-0-0_gv_imputations.dta |
| temp_data | 1 | `adl` | strict_adl_iadl | 1 | 30416 | Limitations with activities of daily living | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta |
| temp_data | 1 | `adl2` | strict_adl_iadl | 1 | 30270 | 1+ adl limitations | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta |
| temp_data | 1 | `adl_f` | strict_adl_iadl | 1 | 30416 | Limitations with activities of daily living - Flag | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta |
| temp_data | 1 | `iadl` | strict_adl_iadl | 1 | 30416 | Limitations with instrumental activities of daily living | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta |
| temp_data | 1 | `iadl2` | strict_adl_iadl | 1 | 30270 | 1+ iadl limitations | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta |
| temp_data | 1 | `iadl_f` | strict_adl_iadl | 1 | 30416 | Limitations with instrumental activities of daily living - Flag | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1.dta |
| temp_data | 1 | `adl` | strict_adl_iadl | 1 | 30416 | 日常生活活动限制 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1_CN.dta |
| temp_data | 1 | `iadl` | strict_adl_iadl | 1 | 30416 | 工具性日常生活活动限制 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1_CN.dta |
| temp_data | 1 | `iadl2` | strict_adl_iadl | 1 | 30270 | 1+ iadl 限制 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Temp_data/share_wave1_CN.dta |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****ADL/房间里行走是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:118 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****ADL/穿衣是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:122 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var batha "ADL/洗澡是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1220 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var beda "ADL/上下床是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1221 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var dressa "ADL/穿衣是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1243 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var eata "ADL/吃饭是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1252 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****ADL/洗澡是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:126 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var housewka "IADL/房屋和花园周围工作是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1267 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var laundrya "IADL/洗衣服是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1280 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var leavhsa "IADL/独自离开房屋和使用交通工具是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1282 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var mapa "IADL/使用地图是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1289 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var mealsa "IADL/准备饭菜是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1291 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var medsa "IADL/服用药物是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1292 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var moneya "IADL/理财是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1296 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****ADL/吃饭是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:130 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var phonea "IADL/使用电话是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1312 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****ADL/上下床是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:134 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****ADL/上厕所是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:138 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var shopa "IADL/购买杂货是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1382 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var toilta "ADL/上厕所是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1393 |
| dofile |  | `` | strict_adl_iadl | 1 |  | label var walkra "ADL/房间里行走是否困难" | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:1402 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****IADL/使用电话是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:142 |
| dofile |  | `` | strict_adl_iadl | 1 |  | *****IADL/服用药物是否困难 | /mnt/e/Database/七大老年健康数据库数据/7.SHARE 欧洲/SHARE_欧洲/Dofiles/no.9_数据合并.do:146 |
