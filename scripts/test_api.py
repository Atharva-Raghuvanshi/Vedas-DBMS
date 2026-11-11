"""End-to-end test of the Flask API against the real MySQL schema.

Run with the backend up:  ./venv/Scripts/python.exe scripts/test_api.py
Covers every endpoint, the four roles, and the negative paths
(401 no token, 403 wrong role, MySQL 1142/1143/1062 mapped to readable
messages). Cleans up everything it creates (as admin).
"""
import json
import urllib.error
import urllib.request

BASE = "http://localhost:5000/api"
PW = "changeme"
results = []


def call(method, path, token=None, body=None, expect=200):
    req = urllib.request.Request(BASE + path, method=method)
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = None
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(req, data=data) as r:
            code, payload = r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        code, payload = e.code, json.loads(e.read())
    ok = code == expect
    line = (f"{method:6s} {path}", code, expect, ok,
            payload.get("message", "") if isinstance(payload, dict)
            else "")
    results.append(line)
    _print(line)
    return payload


def check(label, ok, detail=""):
    line = (label, "-", "-", ok, detail)
    results.append(line)
    _print(line)


def _print(line):
    label, code, expect, ok, detail = line
    mark = "PASS" if ok else "FAIL"
    extra = f" [{code}{'/' + str(expect) if code != expect else ''}]"
    if detail:
        extra += f" {detail}"
    print(f"{mark}  {label}{extra}", flush=True)


# ---------------- logins ----------------
S = call("POST", "/auth/login", body={"role": "student", "password": PW})
E = call("POST", "/auth/login", body={"role": "editor", "password": PW})
SC = call("POST", "/auth/login", body={"role": "scholar", "password": PW})
A = call("POST", "/auth/login", body={"role": "admin", "password": PW})
check("login all four roles",
      all(k in S and k in E and k in SC and k in A for k in ("token",)),
      f"student={S.get('username')} scholar={SC.get('username')} "
      f"editor={E.get('username')} admin={A.get('username')}")
s, e, sc, a = S["token"], E["token"], SC["token"], A["token"]

call("POST", "/auth/login", body={"role": "student", "password": "wrong"},
     expect=401)
call("GET", "/student/mantras", expect=401)                    # no token
call("GET", "/admin/reports/mantras_per_veda", token=s, expect=403)

# ---------------- options ----------------
for kind in ("veda", "kanda", "sukta", "rishi", "deity", "theme", "metre"):
    rows = call("GET", f"/options/{kind}", token=s)
    check(f"options/{kind} non-empty", len(rows) > 0, f"{len(rows)} rows")

# ---------------- student ----------------
r = call("GET", "/student/mantras?page=1&size=10", token=s)
check("student search p1", len(r["rows"]) == 10 and r["pages"] >= 7,
      f"total={r['total']} pages={r['pages']}")
r = call("GET", "/student/mantras?page=7&size=50", token=s)
check("student search last page", len(r["rows"]) == r["total"] - 300,
      f"rows={len(r['rows'])} total={r['total']}")
r = call("GET", "/student/mantras?deity=Agni&size=5", token=s)
check("student filter deity=Agni",
      all("Agni" in (x["deity_name"] or "") for x in r["rows"])
      and len(r["rows"]) == 5, f"{len(r['rows'])} rows")
r = call("GET", "/student/mantras?kanda=3&sukta=62", token=s)
check("student filter kanda+sukta (Gayatri sukta)",
      any(x["mantra_id"] == 16 for x in r["rows"]),
      f"ids={[x['mantra_id'] for x in r['rows']]}")
r = call("GET", "/student/mantras?theme=fire&size=100", token=s)
check("student filter theme=fire", len(r["rows"]) >= 14, f"{len(r['rows'])}")
r = call("GET", "/student/mantras?word=%E0%A4%85%E0%A4%97%E0%A5%8D%E0%A4%A8%E0%A4%BF",
         token=s)   # 'अग्नि'
check("student Sanskrit word search", len(r["rows"]) >= 1, f"{len(r['rows'])}")

call("POST", "/student/bookmarks", token=s, body={"mantra_id": 300})
r = call("GET", "/student/bookmarks", token=s)
check("bookmark added + listed",
      any(x["mantra_id"] == 300 for x in r["rows"]), f"{len(r['rows'])} rows")
call("POST", "/student/bookmarks", token=s, body={"mantra_id": 300},
     expect=409)                                    # duplicate PK
call("DELETE", "/student/bookmarks/300", token=s)
call("DELETE", "/student/bookmarks/300", token=s, expect=404)
r = call("GET", "/student/demo-denied", token=s)
check("student edit blocked (1142 readable)", r.get("denied") is True,
      r.get("message", ""))

# ---------------- scholar ----------------
call("POST", "/scholar/words", token=sc,
     body={"mantra_id": 300, "word_order": 1, "sanskrit_word": "táparti",
           "dhatu": "tṛp-", "english_meaning": "satisfies (api test)"})
r = call("GET", "/scholar/words?mantra_id=300", token=sc)
check("scholar sees word", len(r["rows"]) == 1, f"{len(r['rows'])} rows")
call("PUT", "/scholar/words", token=sc,
     body={"mantra_id": 300, "word_order": 1,
           "english_meaning": "satisfies (edited)"})
call("POST", "/scholar/words", token=sc,
     body={"mantra_id": 300, "word_order": 1, "sanskrit_word": "dup"},
     expect=409)                                    # UNIQUE(mantra,order)

# ---------------- editor ----------------
r = call("GET", "/editor/mantras?page=2&size=10", token=e)
check("editor mantras p2", len(r["rows"]) == 10 and r["total"] >= 333,
      f"total={r['total']}")
r = call("GET", "/editor/mantras?search=Gayatri&page=1&size=5", token=e)
check("editor search metre text", len(r["rows"]) == 5, f"{len(r['rows'])}")

# add a fresh mantra: sukta from the dropdown endpoint (as the UI does),
# mantra_number 99 so the UNIQUE(sukta_id, mantra_number) test is the only
# way it can collide
opts = call("GET", "/options/sukta", token=e)
sukta_id = opts[-1]["item_id"]
r = call("POST", "/editor/mantras", token=e,
         body={"sukta_id": sukta_id, "rishi_id": 1, "deity_id": 2,
               "mantra_number": 99, "metre": "Trishtubh",
               "sanskrit_text": "api test mantra", "iast_text": "api test"})
new_mid = r.get("mantra_id")
check("editor add mantra", bool(new_mid), f"id={new_mid}")
call("POST", "/editor/mantras", token=e,
     body={"sukta_id": sukta_id, "rishi_id": 1, "deity_id": 2,
           "mantra_number": 99}, expect=409)        # UNIQUE(sukta,number)

r = call("POST", "/editor/translations", token=e,
         body={"mantra_id": new_mid, "translator_name": "api-test",
               "text": "api test translation"})
new_tid = r.get("translation_id")
check("editor add pending translation", bool(new_tid),
      f"id={new_tid}")
call("POST", "/editor/translations", token=e,
     body={"mantra_id": new_mid}, expect=400)       # missing fields

r = call("POST", f"/editor/mantras/{new_mid}/edit", token=e,
         body={"sanskrit_text": "api test edited", "iast_text": None})
check("editor transactional edit", "Mantra_History" in r.get("message", ""),
      r.get("message", ""))

# editor cannot approve (403 route gate) - MySQL would also deny (1143)
call("POST", f"/admin/translations/{new_tid}/approve", token=e, expect=403)

# ---------------- lock demo ----------------
r = call("POST", "/editor/lock/start", token=e, body={"mantra_id": new_mid})
check("lock start", "locked" in r.get("message", ""), r.get("message", ""))
call("POST", "/editor/lock/start", token=e, body={"mantra_id": 2},
     expect=409)                                    # already holding
r = call("POST", "/editor/lock/commit", token=e)
check("lock commit", "released" in r.get("message", ""), r.get("message", ""))
call("POST", "/editor/lock/commit", token=e, expect=404)   # none held

# ---------------- admin ----------------
r = call("GET", "/admin/translations?status=pending", token=a)
check("admin pending list", any(x["translation_id"] == new_tid
                                for x in r["rows"]), f"{len(r['rows'])} rows")
r = call("POST", f"/admin/translations/{new_tid}/approve", token=a)
check("admin approve", "approved" in r.get("message", ""), r.get("message", ""))

for key in ("mantras_per_veda", "mantras_per_rishi", "mantras_per_deity",
            "translations_per_translator", "suktas_without_translation",
            "structure_per_veda"):
    r = call("GET", f"/admin/reports/{key}", token=a)
    check(f"report {key}", len(r["rows"]) > 0, f"{len(r['rows'])} rows")

# CRUD: add a theme, use it, delete it
r = call("POST", "/admin/themes", token=a, body={"theme_name": "api-test"})
theme_id = r.get("id")
call("POST", f"/admin/mantras/{new_mid}/themes", token=a,
     body={"theme_id": theme_id})
r = call("GET", f"/admin/mantras/{new_mid}/themes", token=a)
check("theme tagged", theme_id is not None and any(
    t["theme_id"] == theme_id for t in r.get("rows", [])),
    f"{len(r.get('rows', []))} themes")
call("DELETE", f"/admin/mantras/{new_mid}/themes/{theme_id}", token=a)
call("DELETE", f"/admin/themes/{theme_id}", token=a)

r = call("GET", "/admin/history?mantra_id=" + str(new_mid), token=a)
check("mantra history recorded", len(r["rows"]) >= 1,
      f"{len(r['rows'])} rows, by={r['rows'][0]['changed_by'] if r['rows'] else '-'}")

# FK RESTRICT: mantra 1 is bookmarked -> deleting its sukta must map to 409
call("DELETE", "/admin/suktas/1", token=a, expect=409)

# ---------------- cleanup (admin) ----------------
call("DELETE", "/admin/words/300/1", token=a)               # scholar test word
call("DELETE", "/admin/translations/" + str(new_tid), token=a)
call("DELETE", "/admin/history/" + str(new_mid), token=a)   # FK order
call("DELETE", "/admin/mantras/" + str(new_mid), token=a)
call("POST", "/auth/logout", token=s)
call("GET", "/student/mantras", token=s, expect=401)        # token dead

# ---------------- report ----------------
fails = [r for r in results if not r[3]]
for label, code, expect, ok, detail in results:
    mark = "PASS" if ok else "FAIL"
    extra = f" [{code}{'/' + str(expect) if code != expect else ''}]"
    if detail:
        extra += f" {detail}"
    print(f"{mark}  {label}{extra}")
print(f"\n{len(results)} checks, {len(fails)} failures")
raise SystemExit(1 if fails else 0)
