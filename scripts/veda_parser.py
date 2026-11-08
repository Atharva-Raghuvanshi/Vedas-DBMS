"""Parser for the raw veda.txt dump of siddharthjadhav6565/vedas (Rigveda,
Griffith 1895 translation converted from a book PDF).

File structure:
  1.1 Mandala 1                          <- chapter header (skip)
  1.1.1 Mantra 1 – Agni (Author: Madhucchandas Vaisvamitra)   <- hymn heading
  1 I glorify Agni, the divine Priest...  <- numbered verses = mantras
  ...
Boilerplate to skip: page headers/footers, bare page numbers, blank lines.

In this book each "Mantra N" heading is really a SUKTA (hymn) and the
numbered verses inside it are the mantras - that maps onto our schema:
mandala -> Kanda, hymn -> Sukta, verse -> Mantra.
"""
import re

HEADING = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s+Mantra\s+(\d+)\s+[–-]\s+(.*)$")
BOILER = (
    "Ano Bhadraha Kritavayo Yantu Vishwataha",
    "Vishva Dharma ki Jay!",
)


def _clean_heading(rest):
    """'Agni (Author: Madhucchandas Vaisvamitra)' -> (deity, rishi)."""
    if "(" in rest:
        deity_part, author_part = rest.split("(", 1)
    else:
        deity_part, author_part = rest, ""
    deity = deity_part.strip(" ,;–-")
    rishi = author_part.strip()
    rishi = re.sub(r"^Authors?\s*:\s*", "", rishi)
    rishi = rishi.rstrip(")").strip(" .;")
    return deity or "Unknown", rishi or "Unknown"


def parse(path, max_mantras=None):
    """Return a list of mantra dicts:
    {veda_no, mandala, hymn, verse, deity, rishi, text}
    """
    records = []
    cur = None          # (veda_no, mandala, hymn, deity, rishi)
    verse_no = None
    verse_lines = []

    def flush():
        nonlocal verse_no, verse_lines
        if cur and verse_no and verse_lines:
            text = " ".join(verse_lines).strip()
            if text:
                records.append(dict(veda_no=cur[0], mandala=cur[1],
                                    hymn=cur[2], verse=verse_no,
                                    deity=cur[3], rishi=cur[4], text=text))
        verse_no, verse_lines = None, []

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(BOILER) or line.isdigit():
                continue                                  # page furniture
            m = HEADING.match(line)
            if m:
                flush()
                deity, rishi = _clean_heading(m.group(5))
                cur = (int(m.group(1)), int(m.group(2)),
                       int(m.group(3)), deity, rishi)
                continue
            if re.match(r"^\d+\.\d+\s+Mandala\s+\d+$", line):
                flush()
                continue                                  # chapter header
            if cur is None:
                continue                                  # intro before hymns
            vm = re.match(r"^(\d{1,3})\s+(.*)$", line)
            if vm:
                flush()
                verse_no, verse_lines = int(vm.group(1)), [vm.group(2)]
            elif verse_no is not None:
                verse_lines.append(line)                  # wrapped verse
            if max_mantras and len(records) >= max_mantras:
                break
    flush()
    return records


def validate(records):
    """Warn about verse-number gaps inside a hymn (parse quality check)."""
    seen = {}
    problems = 0
    for r in records:
        key = (r["veda_no"], r["mandala"], r["hymn"])
        prev = seen.get(key, 0)
        if r["verse"] != prev + 1:
            problems += 1
        seen[key] = max(prev, r["verse"])
    return problems
