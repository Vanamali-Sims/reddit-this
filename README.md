# NEM Forecast Observatory

Calibrated predictive distributions on top of AEMO's P5MIN point forecast.
Public scoring, battery-dollar translation, leakage-proof bitemporal store.

This repo is a pivot from the previous Reddit search app. Application code
comes in later phases. Right now this is **Phase 0 only**: verified archive
layout plus a throwaway bulk downloader.

See `buildPlan.Md` for the full plan. Archive facts: `docs/ARCHIVE.md`.

## Phase 0 — bulk archive download

Stdlib only. No database. Fetches the last 12 complete months of Phase 1
reports into `data/raw/`.

```powershell
python scripts/bulk_download.py
```

Progress:

```powershell
Get-Content logs/bulk_download.log -Wait
```

The downloader is resumable: matching local size is a skip; partial files
resume with HTTP Range. Safe to re-run.
