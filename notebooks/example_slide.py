"""Fetch one file out of the published example archive, without downloading it all.

The archive on Zenodo holds eight slides and their assays and is about two
gigabytes. This notebook needs one slide out of it. Zip keeps a directory of
its members at the end of the file, and Zenodo serves ranged requests, so the
directory can be read on its own, and one member pulled out by its byte span
and inflated as it arrives. Five requests, and about a tenth of the
archive crosses the wire.

Nothing here is specific to Aurora.

The data
--------
Dawo, S., Nonchev, K., & Silina, K. (2025). *10x Visium Spatial
Transcriptomics Dataset: Kidney (3) and Lung (5) Cancer with Tertiary Lymphoid
Structures* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.14620362
"""

from __future__ import annotations

import json
import struct
import sys
import time
import urllib.error
import urllib.request
import zlib
from dataclasses import dataclass
from pathlib import Path

RECORD = "14620362"
"""The Zenodo record the example slide is published in."""

DOI = "10.5281/zenodo.14620362"
"""Cite this, not the URL: a DOI outlives a hostname."""

ARCHIVE = "TLS_VISIUM_USZ.zip"
"""The record's one file."""

CITATION = (
    "Dawo, S., Nonchev, K., & Silina, K. (2025). 10x Visium Spatial "
    "Transcriptomics Dataset: Kidney (3) and Lung (5) Cancer with Tertiary "
    f"Lymphoid Structures [Data set]. Zenodo. https://doi.org/{DOI}"
)

SLIDE_MEMBER = "TLS_VISIUM_USZ/tif_slides/LC1.tif"
"""The lung-cancer section this notebook runs on."""

_API = "https://zenodo.org/api/records"

_EOCD = b"PK\x05\x06"
_EOCD64_LOCATOR = b"PK\x06\x07"
_EOCD64 = b"PK\x06\x06"
_CENTRAL = b"PK\x01\x02"
_LOCAL = b"PK\x03\x04"

_DEFLATED = 8
_STORED = 0


class ArchiveUnreadable(RuntimeError):
    """The archive did not answer the way a zip served over HTTP has to."""


@dataclass(frozen=True)
class Member:
    """Where one member sits in the archive, and what it should inflate to."""

    name: str
    header_offset: int
    compressed_size: int
    size: int
    method: int
    crc: int


def content_url(record: str = RECORD, archive: str = ARCHIVE) -> str:
    """The published bytes of one file of one record."""
    return f"{_API}/{record}/files/{archive}/content"


def _open_range(url: str, start: int, end: int, *, attempts: int = 5, timeout: float = 120.0):
    """One ranged GET, retried on the rate limit rather than abandoned."""
    for attempt in range(attempts):
        request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt + 1 < attempts:
                time.sleep(10 * (attempt + 1))
                continue
            raise
        if response.status != 206:
            raise ArchiveUnreadable(
                f"the host answered {response.status} for a ranged request, so it is "
                "serving the whole file rather than the span asked for; this helper "
                "cannot take one member out of it"
            )
        return response
    raise ArchiveUnreadable("the host kept refusing ranged requests")


def _read_range(url: str, start: int, end: int) -> bytes:
    with _open_range(url, start, end) as response:
        return response.read()


def _mb(count: int) -> str:
    """Megabytes, with enough decimals that a small file is not reported as nothing."""
    return f"{count / 1e6:,.0f} MB" if count >= 10_000_000 else f"{count / 1e6:.2f} MB"


def archive_size(record: str = RECORD, archive: str = ARCHIVE) -> int:
    """How large the published archive is, as the record itself states it."""
    with urllib.request.urlopen(f"{_API}/{record}", timeout=60) as response:
        metadata = json.load(response)
    for entry in metadata.get("files", []):
        if entry.get("key") == archive:
            return int(entry["size"])
    raise ArchiveUnreadable(f"record {record} publishes no file called {archive!r}")


def _central_directory_span(url: str, size: int) -> tuple[int, int]:
    """Where the member directory starts and how long it is."""
    tail_len = min(size, 66_560)
    tail = _read_range(url, size - tail_len, size - 1)
    start = _end_of_directory(tail)
    cd_size, cd_offset = struct.unpack_from("<12xII", tail, start)
    if cd_offset != 0xFFFFFFFF and cd_size != 0xFFFFFFFF:
        return cd_offset, cd_size
    locator = tail.rfind(_EOCD64_LOCATOR, 0, start)
    if locator < 0:
        raise ArchiveUnreadable("the archive claims 64-bit offsets but carries no locator")
    (eocd64_offset,) = struct.unpack_from("<Q", tail, locator + 8)
    head = _read_range(url, eocd64_offset, eocd64_offset + 55)
    if not head.startswith(_EOCD64):
        raise ArchiveUnreadable("the 64-bit end-of-directory record is not where the locator says")
    cd_size, cd_offset = struct.unpack_from("<QQ", head, 40)
    return cd_offset, cd_size


def _end_of_directory(tail: bytes) -> int:
    """Where the end-of-directory record starts in the archive's last bytes.

    The signature can occur by chance inside the directory it follows, so a
    candidate counts only when the comment length it declares is exactly the
    bytes left after it. Searched from the end, which is where the real one is.
    """
    at = len(tail)
    while True:
        at = tail.rfind(_EOCD, 0, at)
        if at < 0:
            raise ArchiveUnreadable("no end-of-directory record in the last 65 KB of the archive")
        if at + 22 > len(tail):
            continue
        (comment_len,) = struct.unpack_from("<H", tail, at + 20)
        if at + 22 + comment_len == len(tail):
            return at


def list_members(url: str | None = None, size: int | None = None) -> dict[str, Member]:
    """Read the archive's member directory. Two ranged requests, tens of kilobytes."""
    url = url or content_url()
    size = size if size is not None else archive_size()
    cd_offset, cd_size = _central_directory_span(url, size)
    blob = _read_range(url, cd_offset, cd_offset + cd_size - 1)

    members: dict[str, Member] = {}
    at = 0
    while blob.startswith(_CENTRAL, at):
        (
            method, crc, compressed, uncompressed, name_len, extra_len, comment_len, header_offset,
        ) = struct.unpack_from("<10xH4xIIIHHH2x2x4xI", blob, at)
        name = blob[at + 46 : at + 46 + name_len].decode("utf-8", "replace")
        extra = blob[at + 46 + name_len : at + 46 + name_len + extra_len]
        if 0xFFFFFFFF in (compressed, uncompressed, header_offset):
            uncompressed, compressed, header_offset = _zip64(
                extra, uncompressed, compressed, header_offset
            )
        members[name] = Member(name, header_offset, compressed, uncompressed, method, crc)
        at += 46 + name_len + extra_len + comment_len
    if not members:
        raise ArchiveUnreadable("the member directory decoded to nothing")
    return members


def _zip64(extra: bytes, size: int, compressed: int, offset: int) -> tuple[int, int, int]:
    """Replace the fields the 32-bit header could not hold."""
    at = 0
    while at + 4 <= len(extra):
        tag, length = struct.unpack_from("<HH", extra, at)
        body, at = extra[at + 4 : at + 4 + length], at + 4 + length
        if tag != 0x0001:
            continue
        # The 64-bit field carries ONLY the values the 32-bit header could not
        # hold, in this order, so which ones are present is decided by which
        # ones were saturated.
        values = list(struct.unpack_from("<" + "Q" * (len(body) // 8), body))
        if size == 0xFFFFFFFF and values:
            size = values.pop(0)
        if compressed == 0xFFFFFFFF and values:
            compressed = values.pop(0)
        if offset == 0xFFFFFFFF and values:
            offset = values.pop(0)
    return size, compressed, offset


def fetch_member(
    member: str,
    destination: Path | str,
    *,
    url: str | None = None,
    members: dict[str, Member] | None = None,
    progress=print,
) -> Path:
    """Pull one member out of the remote archive and write it out, inflated.

    ONE request for the member's bytes, streamed and inflated as it arrives, so
    the machine never holds the compressed copy and never downloads the rest of
    the archive. The member's own checksum and length are checked before the
    file is moved into place, so a truncated fetch cannot be mistaken for a
    slide.

    Five requests in all, none of them large but the last: the record's
    published size, the archive's last 65 KB, the member directory, the
    member's own thirty-byte header, and the member itself.
    """
    destination = Path(destination)
    if destination.exists():
        progress(f"{destination.name} is already here; nothing fetched.")
        return destination

    url = url or content_url()
    size = archive_size()
    members = members or list_members(url, size)
    if member not in members:
        raise ArchiveUnreadable(f"the archive holds no member called {member!r}")
    entry = members[member]
    if entry.method not in (_STORED, _DEFLATED):
        raise ArchiveUnreadable(f"{member!r} is stored with a compression this helper cannot read")

    head = _read_range(url, entry.header_offset, entry.header_offset + 29)
    if not head.startswith(_LOCAL):
        raise ArchiveUnreadable("the member's own header is not where the directory says it is")
    name_len, extra_len = struct.unpack_from("<HH", head, 26)
    data_at = entry.header_offset + 30 + name_len + extra_len

    progress(
        f"{member}\n"
        f"  {_mb(entry.size)} inflated, {_mb(entry.compressed_size)} over the wire "
        f"(the whole archive is {_mb(size)})."
    )

    inflate = zlib.decompressobj(-zlib.MAX_WBITS) if entry.method == _DEFLATED else None
    partial = destination.with_suffix(destination.suffix + ".part")
    checksum, written, read = 0, 0, 0
    last = time.monotonic()
    with _open_range(url, data_at, data_at + entry.compressed_size - 1) as response:
        with partial.open("wb") as out:
            while True:
                chunk = response.read(1 << 20)
                if not chunk:
                    break
                read += len(chunk)
                block = inflate.decompress(chunk) if inflate else chunk
                if block:
                    out.write(block)
                    checksum = zlib.crc32(block, checksum)
                    written += len(block)
                if time.monotonic() - last > 5:
                    last = time.monotonic()
                    progress(f"  {read / entry.compressed_size:5.1%}", end="\r", flush=True)
            if inflate:
                block = inflate.flush()
                out.write(block)
                checksum = zlib.crc32(block, checksum)
                written += len(block)

    if written != entry.size or checksum != entry.crc:
        partial.unlink(missing_ok=True)
        raise ArchiveUnreadable(
            f"{member!r} arrived as {written} bytes with checksum {checksum:08x}; the archive "
            f"says {entry.size} bytes and {entry.crc:08x}. Nothing was written."
        )
    partial.replace(destination)
    progress(f"  wrote {destination.name} ({_mb(written)}), checksum verified.")
    return destination


if __name__ == "__main__":
    print(CITATION)
    fetch_member(SLIDE_MEMBER, Path(sys.argv[1] if len(sys.argv) > 1 else "LC1.tif"))
