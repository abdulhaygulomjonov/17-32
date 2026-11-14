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
dep = "implementation 'org.tensorflow:tensorflow-lite:2.14.0'"
if dep not in s:
    s, n = re.subn(r"(\ndependencies\s*\{)", lambda m: m.group(1) + "\n    " + dep, s, count=1)
    if n == 0:
        sys.exit("android/app/build.gradle ichida dependencies bloki topilmadi")
open(p, "w", encoding="utf-8").write(s)
print("Gradle moslandi")

# 4) model
if not os.path.exists("nsfw.tflite"):
    sys.exit("nsfw.tflite topilmadi")
os.makedirs("android/app/src/main/assets", exist_ok=True)
shutil.copy("nsfw.tflite", "android/app/src/main/assets/nsfw.tflite")
print("Model joylandi")
