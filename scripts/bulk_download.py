#!/usr/bin/env python3
"""Throwaway MMSDM monthly-archive downloader.

Fetches the last 12 complete months of Phase 1 reports into ./data/raw/.
Stdlib only. Resumable. Safe to re-run.
"""

from __future__ import annotations

import logging
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

BASE = "http://nemweb.com.au/Data_Archive/Wholesale_Electricity/MMSDM"
USER_AGENT = (
    "nem-observatory/0.1 (research; polite MMSDM archive fetch; "
    "contact via GitHub Vanamali-Sims/reddit-this)"
)
CONCURRENCY = 3
MAX_ATTEMPTS = 6
CHUNK = 64 * 1024
MONTHS = 12

# Plan name -> (archive table name, preferred SQLLoader folder).
# P5MIN lives in P5MIN_ALL_DATA so we keep every forecast run, not the
# DATA snapshot. MARKETNOTICE body table is not published publicly —
# we still look for it and download MARKETNOTICETYPE.
REPORTS: dict[str, tuple[str, str]] = {
    "DISPATCHPRICE": ("DISPATCHPRICE", "DATA"),
    "P5MIN": ("P5MIN_REGIONSOLUTION", "P5MIN_ALL_DATA"),
    "DISPATCHREGIONSUM": ("DISPATCHREGIONSUM", "DATA"),
    "ROOFTOP_PV_ACTUAL": ("ROOFTOP_PV_ACTUAL", "DATA"),
    "ROOFTOP_PV_FORECAST": ("ROOFTOP_PV_FORECAST", "DATA"),
    "DISPATCHCONSTRAINT": ("DISPATCHCONSTRAINT", "DATA"),
    "MARKETNOTICE": ("MARKETNOTICEDATA", "DATA"),
    "MARKETNOTICETYPE": ("MARKETNOTICETYPE", "DATA"),
}

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "raw"
LOG_DIR = ROOT / "logs"
LOG_FILE = LOG_DIR / "bulk_download.log"

LISTING_ROW = re.compile(
    r"(?:(?P<dir><dir>|&lt;dir&gt;)|(?P<size>\d[\d,]*))\s*"
    r'<a href="(?P<href>[^"]+)">(?P<name>[^<]+)</a>',
    re.I,
)
MONTH_DIR = re.compile(r"^MMSDM_(\d{4})_(\d{2})/?$", re.I)
YEAR_DIR = re.compile(r"^(\d{4})/?$")
FILE_PART = re.compile(r"^FILE\d+$", re.I)


class _HrefParser(HTMLParser):
    """Fallback if the IIS listing regex misses a row."""

    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[tuple[str, str]] = []
        self._current_href: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._current_href = href
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self._current_href is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._current_href is not None:
            name = "".join(self._buf).strip()
            self.hrefs.append((self._current_href, name))
            self._current_href = None
            self._buf = []


def join_url(folder_url: str, href: str) -> str:
    """Join without urllib.urljoin — it strips # from AEMO filenames."""
    href = href.strip()
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return "http://nemweb.com.au" + href
    return folder_url.rstrip("/") + "/" + href.lstrip("/")


def encode_url(url: str) -> str:
    """Quote # in AEMO filenames. urlsplit would treat them as fragments."""
    scheme, sep, rest = url.partition("://")
    if not sep:
        raise ValueError(f"not an absolute URL: {url}")
    host, _, path = rest.partition("/")
    quoted = urllib.parse.quote(urllib.parse.unquote("/" + path), safe="/")
    return f"{scheme}://{host}{quoted}"


@dataclass(frozen=True)
class RemoteFile:
    report: str
    table: str
    year: int
    month: int
    folder: str
    name: str
    url: str
    size: int

    @property
    def dest(self) -> Path:
        return (
            DEST
            / f"{self.year:04d}"
            / f"MMSDM_{self.year:04d}_{self.month:02d}"
            / self.folder
            / self.name
        )


def setup_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("bulk_download")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


log = setup_logging()


def _sleep_backoff(attempt: int) -> None:
    base = min(2**attempt, 60)
    time.sleep(base + random.uniform(0.2, 1.5))


def http_open(url: str, *, headers: dict[str, str] | None = None, method: str = "GET"):
    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(encode_url(url), headers=hdrs, method=method)
    return urllib.request.urlopen(req, timeout=120)


def fetch_text(url: str) -> str:
    last_err: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            with http_open(url) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            last_err = err
            log.warning("listing retry %s/%s %s (%s)", attempt + 1, MAX_ATTEMPTS, url, err)
            _sleep_backoff(attempt)
    raise RuntimeError(f"failed to fetch listing {url}: {last_err}")


def parse_listing(html: str) -> list[tuple[str, str, int | None, bool]]:
    """Return (href, name, size_or_none, is_dir)."""
    rows: list[tuple[str, str, int | None, bool]] = []
    for match in LISTING_ROW.finditer(html):
        href = match.group("href")
        name = match.group("name").strip()
        is_dir = match.group("dir") is not None
        size = None
        if match.group("size"):
            size = int(match.group("size").replace(",", ""))
        rows.append((href, name, size, is_dir))
    if rows:
        return rows
    parser = _HrefParser()
    parser.feed(html)
    return [(href, name, None, name.endswith("/")) for href, name in parser.hrefs]


def list_year_months() -> list[tuple[int, int]]:
    html = fetch_text(BASE + "/")
    years: list[int] = []
    for _href, name, _size, is_dir in parse_listing(html):
        stem = name.rstrip("/")
        match = YEAR_DIR.match(stem)
        if match and not stem.lower().endswith(".zip"):
            years.append(int(match.group(1)))
    months: list[tuple[int, int]] = []
    for year in sorted(set(years)):
        yhtml = fetch_text(f"{BASE}/{year}/")
        time.sleep(random.uniform(0.3, 0.8))
        for _href, name, _size, is_dir in parse_listing(yhtml):
            stem = name.rstrip("/")
            if stem.lower().endswith(".zip"):
                continue
            match = MONTH_DIR.match(stem)
            if match:
                months.append((int(match.group(1)), int(match.group(2))))
    months = sorted(set(months))
    if len(months) < MONTHS:
        raise RuntimeError(f"expected >= {MONTHS} monthly folders, found {months}")
    chosen = months[-MONTHS:]
    log.info("months to fetch: %s", ", ".join(f"{y:04d}-{m:02d}" for y, m in chosen))
    return chosen


def table_tokens(filename: str) -> set[str]:
    name = filename.upper()
    if name.endswith(".ZIP"):
        name = name[:-4]
    if "#" in name:
        skip = {"PUBLIC_ARCHIVE", "PUBLIC_DVD", "ALL"}
        tokens = []
        for part in name.split("#"):
            if not part or part in skip or FILE_PART.match(part) or part.isdigit():
                continue
            tokens.append(part)
        return set(tokens)
    match = re.match(r"PUBLIC_DVD_(.+)_(\d{12})$", name)
    if match:
        return {match.group(1)}
    return {name}


def matches_table(filename: str, table: str) -> bool:
    return table.upper() in table_tokens(filename)


def discover_files(year: int, month: int) -> list[RemoteFile]:
    month_root = f"{BASE}/{year:04d}/MMSDM_{year:04d}_{month:02d}/MMSDM_Historical_Data_SQLLoader"
    wanted_folders = sorted({folder for _, folder in REPORTS.values()})
    listings: dict[str, list[tuple[str, str, int | None, bool]]] = {}
    for folder in wanted_folders:
        url = f"{month_root}/{folder}/"
        try:
            html = fetch_text(url)
        except RuntimeError as err:
            log.warning("no listing for %s %04d-%02d: %s", folder, year, month, err)
            listings[folder] = []
            continue
        listings[folder] = parse_listing(html)
        time.sleep(random.uniform(0.2, 0.6))

    found: list[RemoteFile] = []
    missing: list[str] = []

    def to_remote(report: str, table: str, folder: str, href: str, name: str, size: int | None) -> RemoteFile:
        folder_url = f"{month_root}/{folder}/"
        return RemoteFile(
            report=report,
            table=table,
            year=year,
            month=month,
            folder=folder,
            name=name,
            url=join_url(folder_url, href),
            size=size or 0,
        )

    for report, (table, folder) in REPORTS.items():
        candidates = [
            to_remote(report, table, folder, href, name, size)
            for href, name, size, is_dir in listings.get(folder, [])
            if not is_dir and name.lower().endswith(".zip") and matches_table(name, table)
        ]
        if not candidates and folder == "P5MIN_ALL_DATA":
            # Fall back to DATA snapshot if ALL is missing this table.
            candidates = [
                to_remote(report, table, "DATA", href, name, size)
                for href, name, size, is_dir in listings.get("DATA", [])
                if not is_dir and name.lower().endswith(".zip") and matches_table(name, table)
            ]
            if candidates:
                log.warning(
                    "%s: P5MIN_ALL_DATA miss for %04d-%02d, using DATA snapshot",
                    table,
                    year,
                    month,
                )
        if not candidates:
            missing.append(f"{report}/{table}")
            continue
        found.extend(candidates)

    if missing:
        log.warning("missing tables %04d-%02d: %s", year, month, ", ".join(missing))
    return found


def download_one(remote: RemoteFile) -> str:
    dest = remote.dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    expected = remote.size

    if dest.exists() and expected and dest.stat().st_size == expected:
        log.info("skip %s %s (%s bytes, already present)", remote.table, dest.name, expected)
        return "skip"

    part = dest.with_suffix(dest.suffix + ".part")
    offset = part.stat().st_size if part.exists() else 0
    if dest.exists() and (not expected or dest.stat().st_size != expected):
        dest.unlink()

    last_err: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            headers = {}
            if offset:
                headers["Range"] = f"bytes={offset}-"
            with http_open(remote.url, headers=headers) as resp:
                status = getattr(resp, "status", 200)
                if offset and status == 200:
                    offset = 0
                mode = "ab" if offset and status == 206 else "wb"
                if mode == "wb":
                    offset = 0
                start = time.time()
                written = offset
                with part.open(mode) as fh:
                    while True:
                        chunk = resp.read(CHUNK)
                        if not chunk:
                            break
                        fh.write(chunk)
                        written += len(chunk)
                elapsed = time.time() - start
            actual = part.stat().st_size
            if expected and actual != expected:
                raise OSError(f"size mismatch: got {actual}, expected {expected}")
            part.replace(dest)
            mbps = (actual - offset) / max(elapsed, 0.001) / 1_000_000
            log.info(
                "got %s %04d-%02d %s (%s bytes, %.1fs, %.2f MB/s)",
                remote.table,
                remote.year,
                remote.month,
                dest.name,
                actual,
                elapsed,
                mbps,
            )
            time.sleep(random.uniform(0.4, 1.2))
            return "ok"
        except (urllib.error.URLError, TimeoutError, OSError) as err:
            last_err = err
            offset = part.stat().st_size if part.exists() else 0
            log.warning(
                "retry %s/%s %s %04d-%02d (%s)",
                attempt + 1,
                MAX_ATTEMPTS,
                remote.table,
                remote.year,
                remote.month,
                err,
            )
            _sleep_backoff(attempt)

    raise RuntimeError(f"download failed {remote.url}: {last_err}")


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    log.info("starting bulk download into %s", DEST)
    log.info("reports: %s", ", ".join(REPORTS))
    months = list_year_months()
    files: list[RemoteFile] = []
    for year, month in months:
        batch = discover_files(year, month)
        log.info(
            "discovered %d files for %04d-%02d (%s)",
            len(batch),
            year,
            month,
            ", ".join(sorted({f.table for f in batch})) or "none",
        )
        files.extend(batch)

    total_bytes = sum(f.size for f in files)
    log.info("queued %d files, %.1f MB", len(files), total_bytes / 1_000_000)
    if not files:
        log.error("nothing to download")
        return 1

    ok = skip = fail = 0
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = {pool.submit(download_one, remote): remote for remote in files}
        for fut in as_completed(futures):
            remote = futures[fut]
            try:
                result = fut.result()
            except Exception as err:  # noqa: BLE001 — log and keep going
                fail += 1
                log.error(
                    "FAIL %s %04d-%02d %s: %s",
                    remote.table,
                    remote.year,
                    remote.month,
                    remote.name,
                    err,
                )
                continue
            if result == "skip":
                skip += 1
            else:
                ok += 1

    log.info("done ok=%s skip=%s fail=%s", ok, skip, fail)
    log.info("progress file: %s", LOG_FILE)
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
