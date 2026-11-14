"""CI da ishlaydi: ochiq NSFW modelini (GantMan/nsfw_model, MobileNetV2 224x224, 5 toifa) yuklab TFLite ga o'giradi.
Natija: native/assets/nsfw.tflite + nsfw_labels.txt. Toifalar tartibi (alifbo): drawings, hentai, neutral, porn, sexy."""
import os, sys, urllib.request

URL = "https://s3.amazonaws.com/ir_public/nsfwjscdn/nsfw_mobilenet2.224x224.h5"
OUT = os.path.join("native", "assets")
os.makedirs(OUT, exist_ok=True)
h5 = "nsfw_mobilenet2.224x224.h5"
if not os.path.exists(h5):
    print("yuklanmoqda:", URL)
    urllib.request.urlretrieve(URL, h5)
print("hajmi:", os.path.getsize(h5))

import tensorflow as tf
import tensorflow_hub as hub

m = tf.keras.models.load_model(h5, custom_objects={"KerasLayer": hub.KerasLayer}, compile=False)
print("kirish:", m.input_shape, "chiqish:", m.output_shape)
conv = tf.lite.TFLiteConverter.from_keras_model(m)
conv.optimizations = [tf.lite.Optimize.DEFAULT]   # dinamik kvantlash: kirish/chiqish float qoladi
data = conv.convert()
open(os.path.join(OUT, "nsfw.tflite"), "wb").write(data)
open(os.path.join(OUT, "nsfw_labels.txt"), "w").write("drawings\nhentai\nneutral\nporn\nsexy\n")

# tekshiruv
it = tf.lite.Interpreter(model_content=data)
it.allocate_tensors()
i, o = it.get_input_details()[0], it.get_output_details()[0]
print("tflite kirish:", i["shape"], i["dtype"], "chiqish:", o["shape"], o["dtype"])
assert list(o["shape"])[-1] == 5, "5 toifa kutilgan edi"
print("tflite hajmi:", len(data))
