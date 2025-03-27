import sys, os, re
from datetime import datetime
import pytest
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, posts_list


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def posts():
    return posts_list

@pytest.fixture
def index_page_elements():
    return [
        """Задание к лабораторной работе""",
        """<p>На странице должны присутствовать следующие элементы:</p>

        <ul class="my-3">
            <li>заголовок поста,</li>
            <li>имя автора,</li>
            <li>дата публикации,</li>
            <li>изображение,</li>
            <li>текст поста,</li>
            <li>форма «Оставьте комментарий» с полем для ввода текста и кнопкой «Отправить»,</li>
            <li>комментарии и ответы на них.</li>
        </ul>

        <p>Все данные должны подставляться в шаблон из приложения.</p>""",
        """<p class="fw-bold">
            2. Добавьте в базовый шаблон подвал (англ. footer) сайта. Укажите там ФИО и номер группы.
        </p>"""
    ]

@pytest.fixture
def posts_page_elements():
    return [
        """<h1 class="my-5">Последние посты</h1>""",
        """<div class="col-md-6 d-flex">
                <div class="card mb-4">
                    <img class="card-img-top" src="""
    ]

@pytest.fixture
def about_page_elements():
    return [
        """<div class="col-md-4 mb-3">
        <img class="avatar""",
        """<div class="col-md-8 text-justify d-flex align-items-center">
        <p>
            Lorem ipsum, dolor sit amet consectetur adipisicing elit. Ea nemo illo natus 
            inventore. Distinctio eius consectetur similique molestias. Molestiae esse maiores 
            enim velit quisquam, omnis libero quam ducimus ea tempore.

            Lorem ipsum dolor sit, amet consectetur adipisicing elit. Exercitationem, ab? 
            Earum cum dolorum ipsum voluptatum quis voluptatibus ea veritatis assumenda aliquid 
            dolores quas, distinctio laboriosam, omnis ratione est tempora nisi.
        </p>
    </div>"""
    ]

# Тесты для проверки использования правильных шаблонов
def test_index_renders_correct_template(client, index_page_elements):
    """Правильный шаблон для главной страницы."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for element in index_page_elements:
        assert element in html

def test_posts_renders_correct_template(client, posts_page_elements):
    """Правильный шаблон для страницы постов."""
    response = client.get('/posts')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for element in posts_page_elements:
        assert element in html
    
def test_about_renders_correct_template(client, about_page_elements):
    """Правильный шаблон для страницы постов."""
    response = client.get('/about')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for element in about_page_elements:
        assert element in html

def test_post_page_renders_correct_template(client, posts):
    """Правильный шаблон для страницы поста."""
    for i in range(len(posts)):
        response = client.get(f'/posts/{i}')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        soup = BeautifulSoup(html, 'html.parser')
        assert soup.find('h1').text == posts[i]['title']
        assert soup.find('div', class_='text-center') is not None


# Тесты для проверки передачи данных в шаблоны
def test_posts_page_receives_all_posts(client, posts):
    """Проверяет, что на страницу со списком постов передаются все посты."""
    response = client.get('/posts')
    html = response.get_data(as_text=True)
    soup = BeautifulSoup(html, 'html.parser')
    post_cards = soup.find_all('div', class_='card')
    assert len(post_cards) == len(posts)

def test_post_page_receives_post_data(client, posts):
    """Проверяет, что на страницу поста передаются все данные поста."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        html = response.get_data(as_text=True)
        assert post['title'] in html
        assert post['author'] in html
        assert post['text'] in html

# Тесты для проверки наличия всех данных поста на странице
def test_post_title_displayed(client, posts):
    """Проверяет, что заголовок поста отображается на странице."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        title = soup.find('h1')
        assert title.text == post['title']

def test_post_author_displayed(client, posts):
    """Проверяет, что имя автора поста отображается на странице."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        author = soup.find('p', class_='text-muted').text.split(', ')[0]
        assert post['author'] == author

def test_post_text_displayed(client, posts):
    """Проверяет, что текст поста отображается на странице."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        text = soup.find('p', class_='main-text')
        assert text.text == post['text']

def test_post_image_displayed(client, posts):
    """Проверяет, что изображение поста отображается на странице."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        image = soup.find('img', class_='img-fluid')
        assert image is not None
        assert post['image_id'] in image['src']

def test_comment_form_displayed(client, posts):
    """Проверяет наличие формы для комментариев на странице поста."""
    for i, _ in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        form = soup.find('form', class_='p-3')
        assert form is not None
        assert form.find('textarea') is not None
        assert form.find('button', class_='btn-primary') is not None

def test_comments_displayed(client, posts):
    """Проверяет, что комментарии к посту отображаются на странице."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        comments = soup.find('div', class_="container d-flex flex-column gap-3").text

        for comment in post['comments']:
            assert comment['author'] in comments
            assert comment['text'] in comments
            for reply in comment.get('replies'):
                assert reply['author'] in comments
                assert reply['text'] in comments

# Тест для проверки формата даты
def test_date_format_is_correct(client, posts):
    """Проверяет, что дата публикации отображается в правильном формате."""
    for i, post in enumerate(posts):
        response = client.get(f'/posts/{i}')
        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
        date_text = soup.find('p', class_='text-muted').text.split(', ')[1]
        assert date_text == post['date'].strftime('%d.%m.%Y')

# Тесты для проверки обработки ошибок
def test_nonexistent_post_returns_404(client):
    """Проверяет, что запрос к несуществующему посту возвращает 404."""
    response_1 = client.get(f'/posts/{len(posts_list)}')
    response_2 = client.get('/posts/-1')
    assert response_1.status_code == 404
    assert response_2.status_code == 404

def test_footer_contains_author_info(client):
    """Проверяет, что в подвале сайта присутствует информация об авторе."""
    response = client.get('/')
    soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
    footer = soup.find('footer')
    assert footer is not None
    assert '231-329' in footer.text
    assert 'Чванов Кирилл' in footer.text