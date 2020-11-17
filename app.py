#-*- coding:utf-8 -*-
# flask 모듈로부터 Flask 함수를 불러온다
# 템플릿 뷰를 사용하기 위한 함수 (jinja2 템플릿 엔진을 통해 html View를 만들어 준다)
# flask 모듈의 request, redirect를 사용하기 위해 불러온다
from flask import Flask, render_template, request, redirect

# 데이터베이스를 사용하기 위해 불러온다
import MySQLdb

config = {
    "user": "root",
    "password": "java1004", 
    "host": "localhost", 
    "database": "pyapp",
    "port": 3306,
    "charset": "utf8"
}

conn = MySQLdb.connect(**config)

# flask에서 해당 모듈이 직접 실행될 수 있게 도와주는 장치
app = Flask(__name__)

# 메시지 목록
@app.route('/', methods=['GET'])
def msg_list():
    cursor = conn.cursor()
    cursor.execute('select msg_id, msg_text from msg')
    msglist = cursor.fetchall()

    print(msglist)

    return render_template('msg_list.html', msglist = msglist)

# 메세지 입력
@app.route('/add_msg', methods=['GET', 'POST'])
def add_msg():
    if request.method == 'GET': # 입력 폼
        return render_template('add_msg.html')
    elif request.method == 'POST':   # 입력 액션
        msg_text = request.form['msg_text']

        # 데이터베이스 입력
        cursor = conn.cursor()
        cursor.execute('insert into msg(msg_text) values(%s)', [msg_text])
        conn.commit()

        return redirect('/')

# 메세지 수정
@app.route('/modify_msg', methods=['GET', 'POST'])
def modify_msg():
    if request.method == 'GET': # 수정 폼
        msg_id = request.args.get('msg_id')

        cursor = conn.cursor()
        cursor.execute('select msg_id, msg_text from msg where msg_id=%s', [msg_id])
        msg = cursor.fetchone()

        print(msg)

        return render_template('modify_msg.html', msg = msg)
    elif request.method == 'POST':   # 수정 액션
        msg_id = request.form['msg_id']
        msg_text = request.form['msg_text']

        # 데이터베이스 입력
        cursor = conn.cursor()
        cursor.execute('update msg set msg_text=%s where msg_id=%s', [msg_text, msg_id])
        conn.commit()

        return redirect('/')

# 메세지 삭제
@app.route('/del_msg', methods=['GET'])
def del_msg():
    msg_id = request.args.get('msg_id')

    # 데이터베이스 삭제
    cursor = conn.cursor()
    cursor.execute('delete from msg where msg_id=%s', [msg_id])
    conn.commit()

    return redirect('/')        

app.run(host='127.0.0.1', port=8880)