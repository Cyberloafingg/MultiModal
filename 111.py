# coding=utf-8

import os
import importlib, sys
importlib.reload(sys)
import time
import subprocess
from flask import request, send_from_directory
from flask import Flask, request, redirect, url_for, render_template
import uuid
import tensorflow.compat.v1 as tf
import pandas as pd

FLAGS = tf.app.flags
from classify_image import run_inference_on_image
from classify_video import extract_video_keyframes

'''
################项目配置信息###################
'''


FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('model_dir', '', """Path to graph_def pb, """)
tf.app.flags.DEFINE_string('model_name', 'my_inception_v4_freeze.pb', '')
tf.app.flags.DEFINE_string('label_file', 'label.txt', '')
tf.app.flags.DEFINE_string('upload_folder', './static', '')  # path of pic
# 这个是音频处理中间产生文件的路径,别再删掉了
tf.app.flags.DEFINE_string('audio_upload_folder', './cache', '')#path of audio
tf.app.flags.DEFINE_integer('num_top_predictions', 5,
                            """Display this many predictions.""")

tf.app.flags.DEFINE_integer('port', '9865',
                            'server with port,if no port, use deault port 80')
tf.app.flags.DEFINE_boolean('debug', False, '')
UPLOAD_FOLDER = FLAGS.upload_folder
Audio_UPLOAD_FOLDER = FLAGS.audio_upload_folder

# 文件格式限制
ALLOWED_EXTENSIONS = set(['jpg', 'JPG', 'jpeg', 'JPEG', 'png', 'mp4','wav','mp3'])


'''
################实例化Flask###################
'''
app = Flask(__name__)
app._static_folder = UPLOAD_FOLDER

'''
################将音频分析在一个子进程启动，不阻塞输出###################
'''
def run(cmd, shell=False) -> (int, str):
    """
    开启子进程，执行对应指令，控制台打印执行过程，然后返回子进程执行的状态码和执行返回的数据
    :param cmd: 子进程命令
    :param shell: 是否开启shell
    :return: 子进程状态码和执行结果
    """
    print('\033[1;32m************** START **************\033[0m') # 使用绿色字体
    p = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = []
    while p.poll() is None:
        line = p.stdout.readline().strip()
        if line:
            line = _decode_data(line)
            result.append(line)
            print('\033[1;35m{0}\033[0m'.format(line))
        # 清空缓存
        sys.stdout.flush()
        sys.stderr.flush()
    # 判断返回码状态
    if p.returncode == 0:
        print('\033[1;32m************** SUCCESS **************\033[0m')
    else:
        print('\033[1;31m************** FAILED **************\033[0m')
    return p.returncode, '\r\n'.join(result)
# 解析IO输出
def _decode_data(byte_data: bytes):
    try:
        return byte_data.decode('UTF-8')
    except UnicodeDecodeError:
        return byte_data.decode('GB18030')


# 该方法检验文件的后缀是否符合上面的要求
def allowed_files(filename):
    return '.' in filename and \
 \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def rename_filename(old_file_name):
    # 找到最后一部分的文件名和后缀
    basename = os.path.basename(old_file_name)
    # 文件名和后缀分离
    name, ext = os.path.splitext(basename)
    # uuid(1生成基于时间戳的随机数避免碰撞
    new_name = str(uuid.uuid1()) + ext

    return new_name


def inference(file_name):
    try:

        predictions, top_k, top_names = run_inference_on_image(file_name)

        print(predictions)

    except Exception as ex:

        print(ex)

        return ""

    new_url = './static/%s' % os.path.basename(file_name)

    image_tag = '<div class="container-fluid pt-5">\
    <div class="container">\
    <div class="text-center pb-2">\
    <p class="section-title px-5"><span class="px-2">Show</span></p>\
    <h1 class="mb-4">识别结果</h1>\
    </div>\
    <div><center><img src="%s"></img><p></center></div>'

    new_tag = image_tag % new_url

    format_string = ''

    for node_id, human_name in zip(top_k, top_names):
        score = predictions[node_id]

        format_string += '<center><h4>%s (score:%.5f)<BR></h4></center>' % (human_name, score)
    # BR表示换行符
    ret_string = new_tag + format_string + '<BR>'

    return ret_string


@app.route("/", methods=['GET', 'POST'])
def root():
    result = render_template("index1.html")
    view = render_template("view.html")
    newresult=render_template("imageresult.html")
    map=render_template("test01.html")
    image_tag = '<div class="container-fluid pt-5">\
        <div class="container">\
        <div class="text-center pb-2">\
        <p class="section-title px-5"><span class="px-2">Show</span></p>\
        <h1 class="mb-4">水鸟栖息地动态分布</h1>\
        </div>'

    if request.method == 'POST':

        file = request.files['file']
        print(file)

        old_file_name = file.filename
        print(old_file_name)

        if file and allowed_files(old_file_name):
            filename = rename_filename(old_file_name)
            print(filename)

            file_path = os.path.join(UPLOAD_FOLDER, filename)
            print(file_path)

            file.save(file_path)

            type_name = 'N/A'

            print('file saved to %s' % file_path)

            out_html = inference(file_path)

            return newresult +out_html+image_tag+'<div  class="container-fluid bg-light position-relative shadow">'+map+'</div>' + view

    return result + view


#@app.route("/about", methods=['GET', 'POST'])
#def about():
#    return render_template("about.html")


# @app.route("/index", methods=['GET', 'POST'])
# def index():
#     return render_template("index.html")


@app.route("/video", methods=['GET', 'POST'])
def video():
    result2 = render_template("video.html")
    view = render_template("view.html")
    newresult2=render_template("videoresult.html")
    if request.method == 'POST':

        file = request.files['file']
        print(file)

        old_file_name = file.filename
        print(old_file_name)
        print(os.path.abspath(old_file_name))
        old_file_name = os.path.abspath(old_file_name)
        print(old_file_name)
        old_file_name = old_file_name.replace('\\', '/')
        print(old_file_name)
        file.save(old_file_name)
        extract_video_keyframes(old_file_name, r'./static')
        old_file_name = 'temporary-image-1.jpg'

        if file and allowed_files(old_file_name):
            filename = 'temporary-image-1.jpg'

            file_path = os.path.join(UPLOAD_FOLDER, filename)

            type_name = 'N/A'

            print('file saved to %s' % file_path)

            out_html = inference(file_path)

            return newresult2 + out_html + view

    return result2 + view


@app.route("/answer", methods=['GET', 'POST'])
def answer():
    return render_template("class.html")


#@app.route("/action", methods=['GET', 'POST'])
#def action():
 #   return render_template("single.html")


@app.route("/wetland", methods=['GET', 'POST'])
def wetland():
    return render_template("wetland.html")


@app.route("/enter", methods=['GET', 'POST'])
def enter():
    return render_template("enter.html")

@app.route("/audio", methods=['GET','POST'])
def audio():
    result3 = render_template("audio.html")
    view = render_template("view.html")
    if request.method == 'POST':
        file = request.files['file']
        file_name = file.filename
        args = request.form
        # print(args)
        cmd = 'python analyze.py --locale zh '
        for arg in args:
            cmd += '--'+ arg +' '+ args[arg] +' '
        # print(cmd)
        # print(file_name)
        base_name = os.path.splitext(file_name)[0]
        # print(base_name)
        if file and allowed_files(file_name):
            filename = file_name
            file_path = os.path.join(Audio_UPLOAD_FOLDER, filename)
            # print(Audio_UPLOAD_FOLDER)
            # print(file_path)
            file.save(file_path)
            print('file saved to %s' % file_path)
            # 在这里启动新的进程，阻塞，仅仅给输出提供异步方法
            return_code, data = run(cmd)
            print('return code:', return_code,'data:', data)
            csv_name = Audio_UPLOAD_FOLDER+'/'+base_name+'.BirdNET.results.csv'
            csv_base_name = base_name+'.BirdNET.results.csv'
            # 读取csv文件
            while not os.path.isfile(Audio_UPLOAD_FOLDER+'/'+base_name+'.BirdNET.results.csv'):
                time.sleep(100)
                print("Please Wait")
            data = pd.read_csv(Audio_UPLOAD_FOLDER+'/'+base_name+'.BirdNET.results.csv', sep=',',encoding='gbk')
            start = data["Start (s)"]
            end = data["End (s)"]
            CN = data["Common name"]
            conf = data["Confidence"]
            title = '<div class="container-fluid pt-5">\
                <div class="container">\
                <div class="text-center pb-2">\
                <p class="section-title px-5"><span class="px-2">Show</span></p>\
                <h1 class="mb-4">识别结果</h1>\
                </div>'
            format_string = ''
            for i in range(len(start)):
                # format_string += f'{start[i]} , {end[i]}, {CN[i]}, {conf[i]} <BR>'
                format_string += '<h4>%s 秒-- %s 秒   \t物种名称：%s \t置信度：%s <BR></h4>' % (start[i],end[i],CN[i],conf[i])
            ret_string = title+format_string + '<BR>'
            os.remove(Audio_UPLOAD_FOLDER+'/'+file_name)
            os.remove(csv_name)
            return result3+ret_string+view
    return result3+view

#192.168.31.62
if __name__ == "__main__":
    print('listening on port %d' % FLAGS.port)
    app.run(host='127.0.0.1', port=FLAGS.port, debug=FLAGS.debug, threaded=True)
