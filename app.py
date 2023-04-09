import subprocess
from flask import Flask, render_template, send_from_directory, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import Length
from flask_wtf.file import FileRequired, FileAllowed
import os
import config
import re

app = Flask(__name__)
app.config.from_object(config)
app.config['UPLOAD_PATH'] = os.path.join(os.getcwd(), 'StegaStamp', 'encode_origin')


# 定义表单
class EncodeUploaderFrom(FlaskForm):
    file = FileField('Upload images!', validators=[FileRequired(), FileAllowed(['png'])])
    msg = StringField('input digital watermarks!', validators=[Length(0, 7)])
    submit = SubmitField('Upload!')


class DecodeUploaderFrom(FlaskForm):
    file = FileField('Upload images!', validators=[FileRequired(), FileAllowed(['png'])])
    submit = SubmitField('Upload!')


class DetectUploaderFrom(FlaskForm):
    file = FileField('Upload videos!', validators=[FileRequired(), FileAllowed(['mp4'])])
    submit = SubmitField('Upload!')


@app.route('/')
def hello():
    return "hello"


@app.route('/encode', methods=['GET', 'POST'])
def encode_upload():
    form = EncodeUploaderFrom()
    if form.validate_on_submit():

        f = form.file.data
        filename = f.filename

        m = form.msg.data

        f.save(os.path.join(os.path.join(os.getcwd(), 'StegaStamp', 'encode_origin'), filename))
        flash('Upload success!')

        return redirect(url_for('encode', filename=filename, msg=m))
    return render_template("encode_upload.html", form=form)
    # 更改操作目录


@app.route('/encode/<path:filename>')
def encode(filename):
    # os.chdir("D:\pycharm-workspace\\flaskStegaStamp\StegaStamp")
    current_path = os.getcwd()
    os.chdir(os.path.join(current_path, "StegaStamp"))
    msg = request.args.get("msg")
    encode_command = f"python encode_image.py saved_models/stegastamp_pretrained --image encode_origin/{filename}" \
                     f" --save_dir ../static --secret {msg}"

    subprocess.getstatusoutput(encode_command)

    m = re.findall('^(.*?).png', filename)

    encoded_filename = m[0] + "_hidden.png"
    # join_res = os.path.join(os.getcwd(), "encode_result", encoded_filename)

    url = url_for("static", filename=encoded_filename)

    return render_template("encode_result.html", url=url)


@app.route('/decode', methods=['GET', 'POST'])
def decode_upload():
    form = DecodeUploaderFrom()
    if form.validate_on_submit():

        f = form.file.data
        filename = f.filename

        f.save(os.path.join(os.path.join(os.getcwd(), 'StegaStamp', 'decode_origin'), filename))
        flash('Upload success!')

        return redirect(url_for('decode', filename=filename))
    return render_template("decode_upload.html", form=form)


@app.route('/decode/<path:filename>')
def decode(filename):
    # os.chdir("D:\pycharm-workspace\\flaskStegaStamp\StegaStamp")
    current_path = os.getcwd()
    os.chdir(os.path.join(current_path, "StegaStamp"))

    decode_command = f"python decode_image.py saved_models/stegastamp_pretrained --image decode_origin/{filename}"

    result = subprocess.getstatusoutput(decode_command)

    result_str = result.__str__()

    r = "^.*?" + filename + "(.*?)$"

    m = re.findall(r, result_str)

    # join_res = os.path.join(os.getcwd(), "encode_result", encoded_filename)

    return render_template("decode_result.html", m=m[0])


@app.route('/detect', methods=['GET', 'POST'])
def detect_upload():
    form = DetectUploaderFrom()
    if form.validate_on_submit():

        f = form.file.data
        filename = f.filename

        f.save(os.path.join(os.path.join(os.getcwd(), 'StegaStamp', 'decode_origin'), filename))
        flash('Upload success!')

        return redirect(url_for('detect', filename=filename))
    return render_template("detect_upload.html", form=form)


@app.route('/detect/<path:filename>')
def detect(filename):
    # os.chdir("D:\pycharm-workspace\\flaskStegaStamp\StegaStamp")
    current_path = os.getcwd()
    os.chdir(os.path.join(current_path, "StegaStamp"))

    m = re.findall('^(.*?).mp4', filename)

    detect_filename = m[0] + "_result.mp4"
    # join_res = os.path.join(os.getcwd(), "encode_result", encoded_filename)

    detect_command = f"python detector.py --detector_model detector_models/stegastamp_detector " \
                     f"--decoder_model saved_models/stegastamp_pretrained --video decode_origin/{filename} " \
                     f"--save_video ../static/{detect_filename}"

    result = subprocess.getstatusoutput(detect_command)

    url = url_for("static", filename=detect_filename)
    # url = url_for("static", filename=filename)
    return render_template("detect_result.html", url=url)


if __name__ == '__main__':
    app.run()
