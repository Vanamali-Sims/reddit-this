# MMSDM archive layout (verified 2026-08-24)

Live listing: <http://nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM/>

No AEMO account is required. The public SQLLoader extracts are open.

## Directory pattern

```
/{year}/MMSDM_{year}_{mm}/MMSDM_Historical_Data_SQLLoader/
    DATA/              # dispatch + most tables
    P5MIN_ALL_DATA/    # full P5MIN run history (use this for P5MIN)
    PREDISP_ALL_DATA/  # not downloaded in Phase 0
```

Year folders also contain a full-month zip (`MMSDM_YYYY_MM.zip`, ~45–64 GB). Do not download those.

As of this check, the newest complete month is **2026-07** (published 2026-08-13). 2026-08 is not on the archive yet.

## File naming

Current scheme (at least 2025-08 through 2026-07):

```
PUBLIC_ARCHIVE#{TABLE}#FILE{nn}#{YYYYMM}010000.zip
```

`#` must be URL-encoded as `%23`. Some tables split across `FILE01`, `FILE02`, … `P5MIN_ALL_DATA` inserts an extra `ALL` token:

```
PUBLIC_ARCHIVE#P5MIN_REGIONSOLUTION#ALL#FILE01#202607010000.zip
```

The older `PUBLIC_DVD_{TABLE}_{YYYYMMDD}0000.zip` names were **not** present in the last 12 months.

## Phase 1 reports — July 2026 sizes

| Report (plan) | Archive table | Folder | July 2026 zip |
|---|---|---|---|
| DISPATCHPRICE | `DISPATCHPRICE` | DATA | 2.1 MB |
| P5MIN | `P5MIN_REGIONSOLUTION` | P5MIN_ALL_DATA | 51.1 MB |
| DISPATCHREGIONSUM | `DISPATCHREGIONSUM` | DATA | 6.2 MB |
| ROOFTOP_PV_ACTUAL | `ROOFTOP_PV_ACTUAL` | DATA | 0.1 MB |
| ROOFTOP_PV_FORECAST | `ROOFTOP_PV_FORECAST` | DATA | 30.5 MB |
| DISPATCHCONSTRAINT | `DISPATCHCONSTRAINT` | DATA | 174.1 MB |
| MARKETNOTICE | `MARKETNOTICETYPE` only | DATA | 1.6 KB |

`MARKETNOTICEDATA` / `MARKETNOTICE` are **not** in the public SQLLoader `DATA` folder (only `MARKETNOTICETYPE`). The downloader will log this and keep looking.

Do not confuse `DISPATCHCONSTRAINT` with `DISPATCH_FCAS_REQ_CONSTRAINT` or `P5MIN_CONSTRAINTSOLUTION` — those are hundreds of MB to tens of GB per month and are not Phase 1 reports.

Rough 12-month total for the Phase 1 set: **~3.3 GB**.
