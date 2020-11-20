#-*- coding:utf-8 -*-
# flask 모듈로부터 Flask 함수를 불러온다
# 템플릿 뷰를 사용하기 위한 함수 (jinja2 템플릿 엔진을 통해 html View를 만들어 준다)
# flask 모듈의 request, redirect를 사용하기 위해 불러온다
from flask import Flask, render_template, request, redirect

# 데이터베이스를 사용하기 위해 불러온다
import pymysql

config = {
    "user": "root",
    "password": "java1004", 
    "host": "localhost", 
    "database": "pyapp",
    "port": 3306,
    "charset": "utf8"
}

conn = pymysql.connect(**config)

# flask에서 해당 모듈이 직접 실행될 수 있게 도와주는 장치
app = Flask(__name__)

# 메시지 목록
@app.route('/', methods=['GET'])
def msg_list():
    # 기본적으로 1 페이지 출력
    current_page = 1

    # 만약 request로 current_page를 받는다면 그 값으로 수정
    if (request.args.get('current_page') != None):
        current_page = int(request.args.get('current_page'))

    # 한 페이지당 데이터를 표시할 개수
    row_per_page = 10

    # SQL 시작 데이터 계산
    begin_row = (current_page - 1) * row_per_page;

    cursor = conn.cursor()
    cursor.execute('select msg_id, msg_title, msg_writer, msg_date, msg_count from msg order by msg_id desc limit %s, %s', [begin_row, row_per_page])
    msglist = cursor.fetchall()

    # 전체 데이터 수
    cursor.execute('select count(*) from msg')
    total_count = cursor.fetchone()

    # 튜플로 받은 total_count를 list로 바꾼 후 다시 일반 변수로 변경
    total_count = list(total_count)
    total_count = total_count[0]

    last_page = int(total_count / row_per_page)

    # 10 미만의 개수의 데이터가 있는 페이지를 표시
    if total_count % row_per_page != 0:
        last_page += 1
    
    # 전체 페이지가 0개이면 현재 페이지도 0으로 표시
    if last_page == 0:
        current_page = 0

    # 내비게이션에 표시할 페이지 수
    nav_per_page = 10

    # 내비게이션 첫 번째 페이지
    nav_first_page = current_page - (current_page % nav_per_page) + 1

    # 내비게이션 마지막 페이지
    nav_last_page = nav_first_page + nav_per_page - 1

    # 내비게이션 번호가 10으로 나누어 떨어지는 경우 처리하는 코드
    if current_page % nav_per_page == 0 and current_page != 0:
        nav_first_page = nav_first_page - nav_per_page
        nav_last_page = nav_first_page + nav_per_page - 1

    # 현재 페이지에 대한 이전 페이지
    if current_page > 10:
        pre_page =  current_page - (current_page % nav_per_page) + 1 - 10
    else:
        pre_page = 1

    # 현재 페이지에 대한 다음 페이지
    next_page = current_page - (current_page % nav_per_page) + 1 + 10
    if next_page > total_count:
        next_page = total_count

    # 내비게이션 페이지 리스트
    nav_bar = []
    for i in range(nav_first_page, nav_last_page + 1):
        nav_bar.append(i)

    return render_template('msg_list.html',
        msglist = msglist,
        current_page = current_page,
        last_page = last_page,
        pre_page = pre_page,
        next_page = next_page,
        nav_bar = nav_bar
    )

# 메세지 내용
@app.route('/msg_view', methods=['GET'])
def msg_view():
    # primary_key인 msg_id를 토대로 작성자, 제목, 내용 데이터를 불러온다
    msg_id = request.args.get('msg_id')

    cursor = conn.cursor()

    # 조회수를 1씩 더한다
    cursor.execute('update msg set msg_count=msg_count+1 where msg_id=%s', [msg_id])

    # commit을 통해 실제 데이터에 최종적으로 반영한다
    conn.commit()

    # 메세지 내용 출력
    cursor.execute('select msg_id, msg_count, msg_date, msg_modifydate, msg_writer, msg_title, msg_text from msg where msg_id=%s', [msg_id])
    msg = cursor.fetchone()

    return render_template('msg_view.html', msg = msg)

# 메세지 입력
@app.route('/add_msg', methods=['GET', 'POST'])
def add_msg():
    if request.method == 'GET': # 입력 폼
        return render_template('add_msg.html')
    elif request.method == 'POST':   # 입력 액션
        msg_writer = request.form['msg_writer']
        msg_title = request.form['msg_title']
        msg_text = request.form['msg_text']

        # 데이터베이스 입력
        cursor = conn.cursor()
        cursor.execute('insert into msg(msg_writer, msg_title, msg_text, msg_date, msg_modifydate, msg_count) values(%s, %s, %s, now(), now(), 0)', [msg_writer, msg_title, msg_text])
        
        # commit을 통해 실제 데이터에 최종적으로 반영한다
        conn.commit()

        return redirect('/')

# 메세지 수정
@app.route('/modify_msg', methods=['GET', 'POST'])
def modify_msg():
    if request.method == 'GET': # 수정 폼
        # primary_key인 msg_id를 토대로 작성자, 제목, 내용 데이터를 불러온다
        msg_id = request.args.get('msg_id')

        cursor = conn.cursor()
        cursor.execute('select msg_id, msg_writer, msg_title, msg_text from msg where msg_id=%s', [msg_id])
        msg = cursor.fetchone()

        return render_template('modify_msg.html', msg = msg)
    elif request.method == 'POST':   # 수정 액션
        msg_id = request.form['msg_id']
        msg_writer = request.form['msg_writer']
        msg_title = request.form['msg_title']
        msg_text = request.form['msg_text']

        # 데이터베이스 입력
        cursor = conn.cursor()
        cursor.execute('update msg set msg_modifydate=now(), msg_writer=%s, msg_title=%s ,msg_text=%s where msg_id=%s', [msg_writer, msg_title, msg_text, msg_id])

        # commit을 통해 실제 데이터에 최종적으로 반영한다
        conn.commit()

        return redirect('/msg_view?msg_id=' + msg_id)

# 메세지 삭제
@app.route('/del_msg', methods=['GET'])
def del_msg():
    msg_id = request.args.get('msg_id')

    # 데이터베이스 삭제
    cursor = conn.cursor()
    cursor.execute('delete from msg where msg_id=%s', [msg_id])
    conn.commit()

    return redirect('/')        

app.run(host='0.0.0.0', port=8080)