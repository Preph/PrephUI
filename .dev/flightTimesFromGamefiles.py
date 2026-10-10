#!/usr/bin/env python3
r"""Regenerate PrephUIFlightTimes.lua from the LOCAL game client.

Pure Python, no DLLs: reads the game's local CASC storage (Data/data/*.idx +
data.NNN archives) itself, extracts the TaxiPath and TaxiPathNode DB2 tables,
parses them, and writes the flown length of every route in yards, keyed by
fromNodeID * 10000 + toNodeID. The runtime (QoL.lua) turns length into time.

The output is addon-namespace Lua, not a global: the generated file starts with
`local _, ns = ...` and fills `ns.flightTimerRoutes`, so it must be listed in the
TOC of the same addon as QoL.lua (PrephUIQoL).

The tables are located in the CASC root by file-name hash. If a build's root
doesn't carry those hashes, drop a listfile.csv ("id;path", e.g. the one
wow.export keeps) next to the script and it is used as a fallback.

Usage:
  python flightTimesFromGamefiles.py --game-dir "C:/Games/WoW Forever"
  python flightTimesFromGamefiles.py --game-dir "C:/Games/WoW Forever" --out "PATH"
  python flightTimesFromGamefiles.py --game-dir "C:/Games/WoW Forever" --version # for example 1.15.9.70003 [wow_classic_era], 12.1.0.69933 [wow], 1.60.1.70338 [wow_classic_beta]) 
  python flightTimesFromGamefiles.py --game-dir "C:/Games/WoW Forever" --dump   # column layout only

My command so i can quickly find without having to remember
  python flightTimesFromGamefiles.py --game-dir "C:\Games\Battle.net\World of Warcraft" --version 1.60.1.70338
"""
import argparse
import bisect
import json
import math
import struct
import sys
import zlib
from collections import defaultdict
from pathlib import Path

# Script lives in <root>/.tools, the addon in <root>/PrephUIQoL -> ../PrephUIQoL relative to the script.
OUT = Path(__file__).resolve().parent.parent / "PrephUI" / "PrephUIQoL" / "PrephUIFlightTimes.lua"

# Copyright/metadata block written at the top of the generated Lua file.
LUA_FILE_HEADER = """--[[
    <PrephUI\\PrephUIQoL\\PrephUIFlightTimes.lua>
    Copyright (C) 2026 Prephmage / Prephalia
    All Rights Reserved.

    This software may not be copied, modified, or distributed 
    without the express written permission of the copyright owner.

    -- Additional Metadata --
    Author:  Prephmage / Prephalia
    CurseForge: https://www.curseforge.com/wow/addons/prephui
    GitHub: https://github.com/preph/PrephUI
--]]""".split("\n")

# Column order of each table as stored in the file (the ID column is handled
# separately). Kinds: "u" = integer, "f3" = float[3]. If a client build orders
# or sizes columns differently, run with --dump and adjust here.
TABLES = {
    "TaxiPath": (
        "dbfilesclient/taxipath.db2",
        [("FromTaxiNode", "u"), ("ToTaxiNode", "u"), ("Cost", "u")],
    ),
    "TaxiPathNode": (
        "dbfilesclient/taxipathnode.db2",
        [("Loc", "f3"), ("PathID", "u"), ("NodeIndex", "u"), ("ContinentID", "u"),
         ("Flags", "u"), ("Delay", "u"), ("ArrivalEventID", "u"), ("DepartureEventID", "u")],
    ),
}


# --------------------------------------------------------------------------
# Local CASC reader (pure Python)
# --------------------------------------------------------------------------

def hashlittle2(data):
    """Bob Jenkins lookup3 hashlittle2 -> 64-bit CASC name hash (pc << 32 | pb)."""
    M = 0xFFFFFFFF

    def rot(x, k):
        return ((x << k) | (x >> (32 - k))) & M

    a = b = c = (0xDEADBEEF + len(data)) & M
    i = 0
    while len(data) - i > 12:
        a = (a + int.from_bytes(data[i:i + 4], "little")) & M
        b = (b + int.from_bytes(data[i + 4:i + 8], "little")) & M
        c = (c + int.from_bytes(data[i + 8:i + 12], "little")) & M
        a = (a - c) & M; a ^= rot(c, 4); c = (c + b) & M
        b = (b - a) & M; b ^= rot(a, 6); a = (a + c) & M
        c = (c - b) & M; c ^= rot(b, 8); b = (b + a) & M
        a = (a - c) & M; a ^= rot(c, 16); c = (c + b) & M
        b = (b - a) & M; b ^= rot(a, 19); a = (a + c) & M
        c = (c - b) & M; c ^= rot(b, 4); b = (b + a) & M
        i += 12
    rest = data[i:]
    if rest:
        rest = rest.ljust(12, b"\0")
        a = (a + int.from_bytes(rest[0:4], "little")) & M
        b = (b + int.from_bytes(rest[4:8], "little")) & M
        c = (c + int.from_bytes(rest[8:12], "little")) & M
        c ^= b; c = (c - rot(b, 14)) & M
        a ^= c; a = (a - rot(c, 11)) & M
        b ^= a; b = (b - rot(a, 25)) & M
        c ^= b; c = (c - rot(b, 16)) & M
        a ^= c; a = (a - rot(c, 4)) & M
        b ^= a; b = (b - rot(a, 14)) & M
        c ^= b; c = (c - rot(b, 24)) & M
    return (c << 32) | b


def blte_decode(data):
    if data[:4] != b"BLTE":
        sys.exit("bad BLTE block")
    header_size = struct.unpack_from(">I", data, 4)[0]
    if header_size == 0:
        chunks, pos = [(len(data) - 8, None)], 8
    else:
        count = int.from_bytes(data[9:12], "big")
        chunks = [struct.unpack_from(">II", data, 12 + 24 * i) for i in range(count)]
        pos = header_size
    out = []
    for comp, _raw in chunks:
        block = data[pos:pos + comp]
        pos += comp
        mode, payload = block[:1], block[1:]
        if mode == b"N":
            out.append(payload)
        elif mode == b"Z":
            out.append(zlib.decompress(payload))
        else:
            sys.exit(f"unsupported BLTE chunk mode {mode!r} (encrypted or LZ4)")
    return b"".join(out)


class Encoding:
    """Content key -> encoding key, via the page index (no full table in memory)."""

    def __init__(self, data):
        if data[:2] != b"EN":
            sys.exit("bad encoding file")
        _ver, self.cks, self.eks, cps, _eps, cpc, _epc, _unk, espec = struct.unpack_from(">BBBHHIIBI", data, 2)
        self.data, self.page_size = data, cps * 1024
        index = 22 + espec
        step = self.cks + 16
        self.first = [data[index + i * step: index + i * step + self.cks] for i in range(cpc)]
        self.pages = index + cpc * step

    def lookup(self, ckey):
        i = bisect.bisect_right(self.first, ckey) - 1
        if i < 0:
            return []
        page = self.data[self.pages + i * self.page_size: self.pages + (i + 1) * self.page_size]
        p = 0
        while p < len(page) and page[p]:
            kc = page[p]
            key = page[p + 6: p + 6 + self.cks]
            e = p + 6 + self.cks
            if key == ckey:
                return [page[e + k * self.eks: e + (k + 1) * self.eks] for k in range(kc)]
            p = e + kc * self.eks
        return []


def root_entries(data, interleaved):
    """Yield (fileDataID, contentKey, nameHash|None, localeFlags) from a TSFM root."""
    if data[:4] != b"TSFM":
        sys.exit("unsupported root file (expected TSFM)")
    a, b = struct.unpack_from("<II", data, 4)
    if a <= 0x100:                       # 10.1.7+ header: size, version, counts
        version, pos = b, a
    else:                                # older header: totalFiles, namedFiles
        version, pos = 1, 12
    while pos < len(data):
        if version >= 2:
            n, locale, u1, u2 = struct.unpack_from("<IIII", data, pos)
            flags = u1 | u2 | (data[pos + 16] << 17)
            pos += 17
        else:
            n, flags, locale = struct.unpack_from("<III", data, pos)
            pos += 12
        deltas = struct.unpack_from(f"<{n}i", data, pos)
        pos += 4 * n
        named = not flags & 0x10000000
        if interleaved:
            stride = 24 if named else 16
            recs = [(data[pos + k * stride: pos + k * stride + 16],
                     struct.unpack_from("<Q", data, pos + k * stride + 16)[0] if named else None)
                    for k in range(n)]
            pos += stride * n
        else:
            cks = [data[pos + 16 * k: pos + 16 * k + 16] for k in range(n)]
            pos += 16 * n
            hashes = [None] * n
            if named:
                hashes = struct.unpack_from(f"<{n}Q", data, pos)
                pos += 8 * n
            recs = list(zip(cks, hashes))
        fid = -1
        for delta, (ckey, nhash) in zip(deltas, recs):
            fid += delta + 1
            yield fid, ckey, nhash, locale


class LocalCasc:
    """Reads files out of a local CASC install (Data/data/*.idx + data.NNN)."""

    def __init__(self, game_dir, want_version=None):
        game = Path(game_dir)
        self.data_dir = game / "Data" / "data"
        if not self.data_dir.is_dir():
            sys.exit(f"{self.data_dir} not found - --game-dir must be the folder that contains Data/")

        info = (game / ".build.info").read_text(encoding="utf-8").splitlines()
        cols = [c.split("!")[0] for c in info[0].split("|")]
        rows = [dict(zip(cols, r.split("|"))) for r in info[1:] if r.strip()]
        listing = ", ".join(f"{r.get('Version')} [{r.get('Product', r.get('Branch', '?'))}]" for r in rows)
        if want_version:
            matches = [r for r in rows if r.get("Version", "").startswith(want_version)]
            if not matches:
                sys.exit(f"no build starting with {want_version} in .build.info. Found: {listing}")
            row = matches[0]
        else:
            row = next((r for r in rows if r.get("Active") == "1"), rows[0])
            if len(rows) > 1:
                print(f"note: .build.info lists several builds ({listing}); using {row.get('Version')}. "
                      f"Pick one with --version.")
        self.version = row.get("Version", "unknown")
        bkey = row["Build Key"]
        cfg = game / "Data" / "config" / bkey[:2] / bkey[2:4] / bkey
        conf = {}
        for line in cfg.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition(" = ")
            conf[k.strip()] = v.split()
        self.root_ckey = bytes.fromhex(conf["root"][0])
        enc_ekey = bytes.fromhex(conf["encoding"][1])

        newest = {}                       # newest .idx per bucket
        for f in self.data_dir.glob("*.idx"):
            bucket, ver = int(f.name[:2], 16), int(f.name[2:10], 16)
            if bucket not in newest or ver > newest[bucket][0]:
                newest[bucket] = (ver, f)
        self.idx = [self._load_idx(f) for _, f in newest.values()]

        self.encoding = Encoding(self._read_ekey(enc_ekey))
        self.listfile = {}
        lf = Path(__file__).resolve().parent / "listfile.csv"
        if lf.is_file():
            with open(lf, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    fid, _, path = line.strip().partition(";")
                    if path.lower() in {p for p, _ in TABLES.values()}:
                        self.listfile[path.lower()] = int(fid)
        cache = Path(__file__).resolve().parent / "fdids.json"
        if cache.is_file():
            for path, fid in json.loads(cache.read_text()).items():
                self.listfile.setdefault(path, fid)
        self._root_cache = None

    @staticmethod
    def _load_idx(path):
        d = path.read_bytes()
        for pos in (0x28, 0x20):          # entry block start differs between index revisions
            if pos + 8 <= len(d):
                size = struct.unpack_from("<I", d, pos)[0]
                if size % 18 == 0 and size and pos + 8 + size <= len(d):
                    return d, pos + 8, size
        sys.exit(f"cannot parse {path.name}")

    def _read_ekey(self, ekey):
        key = ekey[:9]
        for d, start, size in self.idx:
            at = d.find(key, start, start + size)
            while at != -1:
                if (at - start) % 18 == 0:
                    off5 = int.from_bytes(d[at + 9:at + 14], "big")
                    enc_size = struct.unpack_from("<I", d, at + 14)[0]
                    archive, offset = off5 >> 30, off5 & 0x3FFFFFFF
                    with open(self.data_dir / f"data.{archive:03d}", "rb") as fh:
                        fh.seek(offset)
                        blob = fh.read(enc_size)
                    return blte_decode(blob[30:])   # 30-byte local header precedes BLTE
                at = d.find(key, at + 1, start + size)
        return None

    def _read_ckey(self, ckey):
        for ekey in self.encoding.lookup(ckey):
            data = self._read_ekey(ekey)
            if data is not None:
                return data
        return None

    def _root_lookup(self):
        """Find the wanted tables in the root; tries both known record layouts."""
        root = self._read_ckey(self.root_ckey)
        if root is None:
            sys.exit("root file not found in local storage")
        by_hash = {hashlittle2(p.replace("/", "\\").upper().encode()): p
                   for p, _ in TABLES.values()}
        by_fid = {fid: p for p, fid in self.listfile.items()}
        report = []
        for interleaved in (True, False):
            found = {}
            total = named = 0
            for fid, ckey, nhash, locale in root_entries(root, interleaved):
                total += 1
                named += nhash is not None
                path = by_hash.get(nhash) or by_fid.get(fid)
                if path and (path not in found or locale & 0x2):   # prefer enUS / all
                    found[path] = ckey
            in_enc = sum(bool(self.encoding.lookup(c)) for c in found.values())
            report.append(f"  layout {'interleaved' if interleaved else 'separate'}: {total} entries, "
                          f"{named} named, {len(found)}/{len(TABLES)} tables matched, {in_enc} present in encoding")
            if len(found) == len(TABLES) and in_enc == len(found):
                return found
        sys.exit("could not locate the TaxiPath tables in the root file:\n" + "\n".join(report) +
                 "\nPut a listfile.csv (id;path) next to the script.")

    def read(self, path):
        if self._root_cache is None:
            self._root_cache = self._root_lookup()
        data = self._read_ckey(self._root_cache[path])
        if data is None:
            sys.exit(f"{path}: data not present in local storage")
        return data

    def close(self):
        pass


# --------------------------------------------------------------------------
# WDC3 / WDC5 parser (only what these two tables need)
# --------------------------------------------------------------------------

def parse_db2(data, layout, label, dump=False):
    magic = data[:4]
    if magic == b"WDC5":
        pos = 4 + 4 + 128          # magic, schema version, schema name
    elif magic == b"WDC3":
        pos = 4
    else:
        sys.exit(f"{label}: unsupported DB2 format {magic!r} (parser handles WDC3/WDC5)")

    (rec_count, field_count, rec_size, _str_size, _thash, _lhash, _min_id, _max_id,
     _locale, flags, id_index, _total_fields, _bp_off, _lookup_cols,
     info_size, common_size, pallet_size, section_count) = struct.unpack_from("<9IHH7I", data, pos)
    pos += 68

    sections = [struct.unpack_from("<Q8I", data, pos + 40 * i) for i in range(section_count)]
    pos += 40 * section_count
    pos += 4 * field_count                                   # field_structure, unused
    infos = [struct.unpack_from("<HHII3I", data, pos + 24 * i) for i in range(info_size // 24)]
    pos += info_size
    pallet = data[pos:pos + pallet_size]
    pos += pallet_size
    common = data[pos:pos + common_size]

    if dump:
        print(f"== {label}: {magic.decode()} records={rec_count} fields={field_count} "
              f"record_size={rec_size} flags={flags:#x} id_index={id_index}")
        for i, (fo, fs, add, st, v1, v2, v3) in enumerate(infos):
            print(f"  col {i}: bit_offset={fo} bits={fs} storage_type={st} extra={add} vals={v1},{v2},{v3}")

    cols = list(layout)
    has_id_list = bool(flags & 4)
    if not has_id_list:
        cols.insert(id_index, ("ID", "u"))
    if len(cols) != field_count or len(infos) != field_count:
        sys.exit(f"{label}: file has {field_count} columns, layout expects {len(cols)}. "
                 f"Run with --dump and fix TABLES at the top of the script.")
    if flags & 1:
        sys.exit(f"{label}: offset-map tables are not supported")

    pallet_at, common_at, common_map = {}, {}, {}
    p = c = 0
    for i, (_, _, add, st, *_r) in enumerate(infos):
        if st in (3, 4):
            pallet_at[i] = p // 4
            p += add
        elif st == 2:
            common_map[i] = {k: v for k, v in struct.iter_unpack("<II", common[c:c + add])}
            c += add
    pallet_words = struct.unpack(f"<{len(pallet) // 4}I", pallet)

    def value(i, rec, rid):
        fo, fs, _add, st, v1, _v2, v3 = infos[i]
        kind = cols[i][1]
        if st == 0:
            raw = (rec >> fo) & ((1 << max(fs, 96 if kind == "f3" else 32)) - 1)
        elif st in (1, 5):
            raw = (rec >> fo) & ((1 << fs) - 1)
            if st == 5 and raw >> (fs - 1):
                raw -= 1 << fs
        elif st == 3:
            raw = pallet_words[pallet_at[i] + ((rec >> fo) & ((1 << fs) - 1))]
        elif st == 4:
            n, base = v3, pallet_at[i] + ((rec >> fo) & ((1 << fs) - 1)) * v3
            raw = tuple(pallet_words[base:base + n])
        else:  # 2: common data, per-ID override of a default
            raw = common_map[i].get(rid, v1)
        if kind == "f3":
            if isinstance(raw, tuple):
                return struct.unpack("<3f", struct.pack("<3I", *raw))
            return struct.unpack("<3f", raw.to_bytes(12, "little"))
        return raw

    rows = []
    for _key, file_off, n, str_size, _oe, idlist_size, _rel, _omc, copy_count in sections:
        rec_end = file_off + n * rec_size
        ids = None
        if idlist_size:
            ids = struct.unpack_from(f"<{n}I", data, rec_end + str_size)
        copy_at = rec_end + str_size + idlist_size
        by_id = {}
        for k in range(n):
            rec = int.from_bytes(data[file_off + k * rec_size: file_off + (k + 1) * rec_size], "little")
            rid = ids[k] if ids else value(id_index, rec, None)
            row = {name: value(i, rec, rid) for i, (name, _) in enumerate(cols)}
            row["ID"] = rid
            by_id[rid] = row
            rows.append(row)
        for k in range(copy_count):
            new_id, orig_id = struct.unpack_from("<II", data, copy_at + 8 * k)
            if orig_id in by_id:
                rows.append({**by_id[orig_id], "ID": new_id})
    return rows


# --------------------------------------------------------------------------
# Route length
# --------------------------------------------------------------------------

def spline_length(pts, steps=16):
    """Length of the Catmull-Rom curve the flight follows through the waypoints."""
    total = 0.0
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        prev = p1
        for s in range(1, steps + 1):
            t = s / steps
            t2, t3 = t * t, t * t * t
            cur = tuple(
                0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (3 * b - a - 3 * c + d) * t3)
                for a, b, c, d in zip(p0, p1, p2, p3)
            )
            total += math.dist(prev, cur)
            prev = cur
    return total


def main():
    ap = argparse.ArgumentParser(description="Regenerate PrephUIFlightTimes.lua from local game files.")
    ap.add_argument("--game-dir", required=True, help="game folder containing Data/ and .build.info")
    ap.add_argument("--version", help="build to read, matched by prefix against .build.info, e.g. 1.60.1")
    ap.add_argument("--build", help="build string for the Lua header (default: from .build.info)")
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--keep-delays", action="store_true", help="also keep paths whose waypoints have a delay")
    ap.add_argument("--verbose", action="store_true", help="list example skipped paths per reason")
    ap.add_argument("--dump", action="store_true", help="print column layout and exit")
    args = ap.parse_args()

    source = LocalCasc(args.game_dir, args.version)
    build = args.build or source.version

    try:
        tables = {name: parse_db2(source.read(path), layout, name, args.dump)
                  for name, (path, layout) in TABLES.items()}
    finally:
        source.close()
    if args.dump:
        return

    paths = {r["ID"]: r for r in tables["TaxiPath"]}
    points = defaultdict(list)
    for r in tables["TaxiPathNode"]:
        points[r["PathID"]].append((r["NodeIndex"], r["ContinentID"], r["Delay"], r["Loc"]))

    if not points or sum(pid in paths for pid in points) < 0.9 * len(points):
        sys.exit("TaxiPathNode.PathID does not match TaxiPath.ID - column layout is probably "
                 "wrong for this build. Run with --dump and adjust TABLES.")

    lengths = {}
    skipped = defaultdict(list)
    for pid, p in paths.items():
        from_node, to_node = p["FromTaxiNode"], p["ToTaxiNode"]
        pts = sorted(points.get(pid, []))
        tag = f"{pid}: {from_node}->{to_node}"
        if len(pts) < 2:
            skipped["fewer than 2 waypoints"].append(tag)
            continue
        # Boat/zeppelin paths stop at docks or cross continents; flight paths don't.
        if len({pt[1] for pt in pts}) > 1:
            skipped["crosses continents"].append(tag)
            continue
        if any(pt[2] for pt in pts) and not args.keep_delays:
            skipped["has waypoint delay (boat/zeppelin)"].append(tag)
            continue
        if not from_node or not to_node:
            skipped["missing from/to node"].append(tag)
            continue
        if from_node >= 10000 or to_node >= 10000:
            sys.exit(f"node id out of key range: {from_node} -> {to_node}")
        key = from_node * 10000 + to_node
        if key in lengths:
            skipped["duplicate from->to (overwritten)"].append(tag)
        lengths[key] = round(spline_length([pt[3] for pt in pts]))

    print(f"build {build}: {len(paths)} TaxiPath rows, {len(lengths)} routes kept")
    for reason, items in skipped.items():
        print(f"  skipped {len(items):4d}  {reason}" + (f"   e.g. {', '.join(items[:5])}" if args.verbose else ""))

    # The table lives in the addon namespace of the addon this file is loaded with (PrephUIQoL):
    # no global is created. QoL.lua reads ns.flightTimerRoutes and converts yards -> seconds.
    lines = LUA_FILE_HEADER + [
        '',
        '',
        '-- Local build ' + build + '.',
        '--',
        '-- Generated by ' + Path(__file__).name + ' - do not edit by hand.',
        '-- Flight route table, exposed through the addon namespace (no global):',
        '--     local _, ns = ...',
        '--     ns.flightTimerRoutes[fromTaxiNodeID * 10000 + toTaxiNodeID]  ->  flown length in YARDS',
        'local _, ns = ...',
        '',
        'ns.flightTimerRoutes = {',
    ]
    for key in sorted(lengths):
        lines.append(f"    [{key}] = {lengths[key]},")
    lines.append("}")
    if not args.out.parent.is_dir():
        sys.exit(f"output folder {args.out.parent} does not exist - run the script from <root>/.tools "
                 f"next to <root>/PrephUIQoL, or pass --out.")
    args.out.write_text("\r\n".join(lines) + "\r\n", encoding="ascii", newline="")
    print(f"{len(lengths)} routes -> {args.out}")


if __name__ == "__main__":
    main()