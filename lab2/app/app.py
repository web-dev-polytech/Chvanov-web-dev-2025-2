import random
from flask import Flask, render_template, abort, make_response, request
from faker import Faker



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

@app.route('/phone', methods=["GET", "POST"])
def phone():
    phone_number = None
    formatted_number = None
    error = None
    
    if request.method == "POST":
        phone_number = request.form.get('phone', '')
        print(phone_number)
        print(type(phone_number))
        print()
        # formatted_number, error = process_phone_number(phone_number)
            
    return render_template(
        'phone.html', 
        error=error
    )