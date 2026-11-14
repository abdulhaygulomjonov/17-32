"""GantMan/nsfw_model release'laridan modelni topib, nsfw.tflite ga aylantiradi.
Ishlatish: python tools/fetch_model.py
Har bir nomzod fayl ketma-ket sinab ko'riladi; birinchi muvaffaqiyatlisi qoladi.
"""
import glob
import json
import os
import subprocess
import sys
import urllib.request
import zipfile

TAGS = ["1.1.0", "1.2.0"]
API = "https://api.github.com/repos/GantMan/nsfw_model/releases/tags/"


def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "17-32-build"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok and "api.github.com" in url:
        req.add_header("Authorization", "Bearer " + tok)
    with urllib.request.urlopen(req, timeout=300) as r:
        data = r.read()
    return data if binary else json.loads(data)


assets = []
for tag in TAGS:
    try:
        rel = get(API + tag)
        for a in rel.get("assets", []):
            assets.append((tag, a["name"], a["browser_download_url"]))
    except Exception as e:
        print("Release o'qilmadi", tag, e)

print("Topilgan fayllar:")
for t, n, u in assets:
    print(" ", t, n, u)


def score(item):
    n = item[1].lower()
    s = 0
    if "224" in n: s += 2
    if "mobilenet" in n: s += 2
    if "tfjs" in n or "min_" in n or "299" in n or "inception" in n: s -= 5
    if n.endswith(".h5") or n.endswith(".zip"): s += 1
    else: s -= 10
    return -s


cands = [a for a in sorted(assets, key=score) if a[1].lower().endswith((".h5", ".zip"))]
os.makedirs("dl", exist_ok=True)

for tag, name, url in cands:
    print("Urinish:", name)
    try:
        path = os.path.join("dl", name)
        open(path, "wb").write(get(url, binary=True))
        targets = []
        if name.lower().endswith(".zip"):
            out = os.path.join("dl", name + "_x")
            zipfile.ZipFile(path).extractall(out)
            targets += [os.path.dirname(p) for p in glob.glob(out + "/**/saved_model.pb", recursive=True)]
            targets += glob.glob(out + "/**/*.h5", recursive=True)
        else:
            targets.append(path)
        for t in targets:
            print("Aylantirish:", t)
            if subprocess.call([sys.executable, "tools/make_model.py", t, "nsfw.tflite"]) == 0:
                print("Tayyor:", t)
                sys.exit(0)
    except Exception as e:
        print("Xato:", e)

sys.exit("Hech bir model aylantirilmadi. nsfw.tflite ni repo ildiziga yuklang.")
