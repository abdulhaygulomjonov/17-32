"""GantMan NSFW (MobileNetV2, 224x224) Keras modelini nsfw.tflite ga aylantiradi.
Chiqish sinflari tartibi: drawings, hentai, neutral, porn, sexy.
Ishlatish: python3 tools/make_model.py nsfw.h5 nsfw.tflite
"""
import sys

import tensorflow as tf
import tensorflow_hub as hub

src = sys.argv[1] if len(sys.argv) > 1 else "nsfw.h5"
dst = sys.argv[2] if len(sys.argv) > 2 else "nsfw.tflite"

m = tf.keras.models.load_model(src, custom_objects={"KerasLayer": hub.KerasLayer}, compile=False)
print("keras:", m.input_shape, m.output_shape)

data = tf.lite.TFLiteConverter.from_keras_model(m).convert()
it = tf.lite.Interpreter(model_content=data)
it.allocate_tensors()
print("tflite in:", it.get_input_details()[0]["shape"], "out:", it.get_output_details()[0]["shape"])
assert it.get_output_details()[0]["shape"][-1] == 5, "kutilgan 5 sinf emas"

open(dst, "wb").write(data)
print("saqlandi:", dst)
