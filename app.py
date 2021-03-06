import os, flask, io, datetime
from werkzeug.utils import secure_filename 

import tensorflow as tf
import numpy as np
from PIL import Image
from flask import request

from model import Network
import db

CKPT_DIR = 'ckpt'

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  

# Load Pre-trained TensorFlow MNIST Model
def loadmodel():
    global net
    net = Network()
    global sess
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state(CKPT_DIR)
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess, ckpt.model_checkpoint_path)
    else:
        raise FileNotFoundError("Unable to find saved model")

# Make Prediction
def predict(image_path):
    img = Image.open(image_path).convert('L')  #Transform to Black&White
    flatten_img = np.reshape(img, 784)
    x = np.array([1 - flatten_img])
    y = sess.run(net.y, feed_dict={net.x: x})
    result = np.argmax(y[0])
    return result

# Add Timestamp to File Name
def parseName(name, time):
    temp = []
    temp.append(str(time))
    temp.append('_')
    temp.append(name)
    name = ''.join(temp)
    return name

# Flask Router
@app.route("/mnist", methods=["POST"])
def mnist():
    req_time = datetime.datetime.now()
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            upload_file = flask.request.files["image"]
            upload_filename = secure_filename((upload_file).filename)

            save_filename = parseName(upload_filename,req_time)
            save_filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], save_filename)
            upload_file.save(save_filepath)
            mnist_result = str(predict(save_filepath))

            db.insertData(request.remote_addr, req_time, save_filepath, mnist_result)

    return ("%s%s%s%s%s%s%s%s%s" % ("Upload File Name: ", upload_filename, "\n", 
                              "Upload Time: ", req_time, "\n",
                              "Prediction: ",mnist_result, "\n"))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    db.createKeySpace()
    loadmodel()
    app.run(debug=True, use_reloader=False, host='0.0.0.0')