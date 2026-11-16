"""native.zip ni android/ ustiga yoyadi, Gradle'ni moslaydi va modelni joylaydi.
Ishlatish (repo ildizidan): python3 tools/apply_native.py
"""
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

if not os.path.isdir("android"):
    sys.exit("android/ papkasi yo'q: avval `npx cap add android` ishlating")

# 1) native fayllarni yoyish (zip ichida yo'llar android/... bilan boshlanadi)
with zipfile.ZipFile("native.zip") as z:
    z.extractall(".")
print("native.zip yoyildi")

# 2) minSdk 26
p = "android/variables.gradle"
s = open(p, encoding="utf-8").read()
s = re.sub(r"minSdkVersion\s*=\s*\d+", "minSdkVersion = 26", s)
open(p, "w", encoding="utf-8").write(s)

# 3) TensorFlow Lite bog'liqligi
p = "android/app/build.gradle"
s = open(p, encoding="utf-8").read()
deps = [
    "implementation 'org.tensorflow:tensorflow-lite:2.14.0'",
    "implementation 'com.microsoft.onnxruntime:onnxruntime-android:1.19.2'",
    "implementation 'com.google.mlkit:text-recognition:16.0.1'",
]
for dep in deps:
    if dep not in s:
        s, n = re.subn(r"(\ndependencies\s*\{)", lambda m: m.group(1) + "\n    " + dep, s, count=1)
        if n == 0:
            sys.exit("android/app/build.gradle ichida dependencies bloki topilmadi")
open(p, "w", encoding="utf-8").write(s)
print("Gradle moslandi")

# 4) model
os.makedirs("android/app/src/main/assets", exist_ok=True)
found = False
for m in ("nudenet.onnx", "nsfw.tflite"):
    if os.path.exists(m):
        shutil.copy(m, os.path.join("android/app/src/main/assets", m))
        print("Model joylandi:", m)
        found = True
if not found:
    sys.exit("Model topilmadi: nudenet.onnx ham, nsfw.tflite ham yo'q")

# 5) ikonka: icon-192.png / icon-512.png -> ilova ikonkasi
src_icon = "icon-512.png" if os.path.exists("icon-512.png") else "icon-192.png"
if os.path.exists(src_icon):
    res = "android/app/src/main/res"
    # Capacitor'ning adaptive (anydpi) ikonkalari PNG ni bosib qolmasligi uchun o'chiriladi
    shutil.rmtree(os.path.join(res, "mipmap-anydpi-v26"), ignore_errors=True)
    sizes = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    try:
        from PIL import Image
        base = Image.open(src_icon).convert("RGBA")
    except Exception:
        base = None
    for dens, px in sizes.items():
        d = os.path.join(res, "mipmap-" + dens)
        os.makedirs(d, exist_ok=True)
        for name in ("ic_launcher.png", "ic_launcher_round.png", "ic_launcher_foreground.png"):
            out = os.path.join(d, name)
            if base is not None:
                base.resize((px, px), Image.LANCZOS).save(out)
            else:
                shutil.copy(src_icon, out)
    print("Ikonka joylandi:", src_icon)
else:
    print("Ikonka topilmadi, standart ikonka qoladi")
