import random
from flask import Flask, render_template, abort, make_response, request, flash, redirect, url_for
from faker import Faker
import re



fake = Faker()

app = Flask(__name__)

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = {
            'author': fake.name(),
            'text': fake.text()
        }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }

posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

@app.route('/posts/<int:index>')
def post(index):
    if not(0 <= index < len(posts_list)):
        # return response with status code 404
        abort(404)

    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')



@app.route('/args')
def args():
    request_args = request.args
    return render_template('request_fields.html', request_fieldname='args', request_dict=request_args)

@app.route('/headers')
def headers():
    request_headers = request.headers
    return render_template('request_fields.html', request_fieldname='headers', request_dict=request_headers)
    
@app.route('/cookies')
def cookies():
    request_cookies = request.cookies
    response = make_response(
        render_template(
            'request_fields.html',
            request_fieldname='cookies',
            request_dict=request_cookies
        )
    )
    if 'name' not in request_cookies:
        response.set_cookie('name', 'Zadira Bob')
    else:
        response.delete_cookie('name')
    
    return response

@app.route('/form', methods=["GET", "POST"])
def form():
    return render_template('form.html')

def _phone_check(phone: str):
    formatless_phone = "".join(filter(str.isdigit, phone))
    patterns = [
        "\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}",
        "8\(\d{3}\)\d{7}",
        "\d{3}\.\d{3}\.\d{2}\.\d{2}"
    ]
    if not any(re.fullmatch(pattern, phone) for pattern in patterns):
        raise ValueError('Недопустимый ввод. В номере телефона встречаются недопустимые символы.')
    if not(((phone.startswith("+7") or phone.startswith("8")) and len(formatless_phone) == 11)\
       or len(formatless_phone) == 10):
        raise ValueError('Недопустимый ввод. Неверное количество цифр.')
    return True
@app.route('/phone', methods=["GET", "POST"])
def phone():
    formatted_number = None
    error = None
    if request.method == "POST":
        phone_number = request.form.get('phone', '').strip()
        try:
            if _phone_check(phone_number):
                formatless_phone = "".join(filter(str.isdigit, phone_number))
                if len(formatless_phone) == 11:
                    formatless_phone = formatless_phone[1:]
                formatted_number = f"8-{formatless_phone[:3]}-{formatless_phone[3:6]}-{formatless_phone[6:8]}-{formatless_phone[8:10]}"
        except ValueError as e:
            error = e
            
    return render_template(
        'phone.html',
        formatted_number=formatted_number,
        error=error
    )