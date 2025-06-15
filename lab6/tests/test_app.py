import os
import sys
import pytest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User, Course, Review, Category, Image
from app.repositories import ReviewRepository


@pytest.fixture
def app():
    test_config = {
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'UPLOAD_FOLDER': '/tmp/test_uploads'
    }
    app = create_app(test_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user():
    return User(
        id=1,
        login='testuser',
        first_name='Тест',
        last_name='Пользователь',
        middle_name='Тестович',
        password_hash='test_hash'
    )


@pytest.fixture
def sample_category():
    return Category(
        id=1,
        name='Программирование',
        parent_id=None
    )


@pytest.fixture
def sample_course():
    return Course(
        id=1,
        name='Основы Python',
        short_desc='Краткое описание',
        full_desc='Полное описание курса',
        rating_sum=0,
        rating_num=0,
        category_id=1,
        author_id=1,
        background_image_id=None,
        created_at=datetime.now()
    )


@pytest.fixture
def sample_review():
    return Review(
        id=1,
        rating=5,
        text='Отличный курс!',
        created_at=datetime.now(),
        course_id=1,
        user_id=1
    )



def test_course_show_page_with_reviews(client, mocker, sample_course, sample_review):
    mock_course_repo = mocker.patch('app.courses.course_repository')
    mock_review_repo = mocker.patch('app.courses.review_repository')
    
    mock_course_repo.get_course_by_id.return_value = sample_course
    mock_review_repo.get_course_page_reviews.return_value.all.return_value = [sample_review]
    mock_review_repo.get_latest_review_by_user.return_value = None
    
    response = client.get('/courses/1')
    assert response.status_code == 200
    assert 'Отличный курс!'.encode('utf-8') in response.data


def test_course_reviews_page(client, mocker, sample_course):
    mock_course_repo = mocker.patch('app.courses.course_repository')
    mock_review_repo = mocker.patch('app.courses.review_repository')
    
    mock_course_repo.get_course_by_id.return_value = sample_course
    mock_pagination = mocker.MagicMock()
    mock_pagination.items = []
    mock_review_repo.get_pagination_info.return_value = mock_pagination
    mock_review_repo.get_all_course_reviews.return_value = []
    mock_review_repo.get_latest_review_by_user.return_value = None
    
    response = client.get('/courses/1/reviews')
    assert response.status_code == 200
    mock_course_repo.get_course_by_id.assert_called_once_with(1)


def test_course_reviews_page_with_sort(client, mocker, sample_course):
    mock_course_repo = mocker.patch('app.courses.course_repository')
    mock_review_repo = mocker.patch('app.courses.review_repository')
    
    mock_course_repo.get_course_by_id.return_value = sample_course
    mock_pagination = mocker.MagicMock()
    mock_pagination.items = []
    mock_review_repo.get_pagination_info.return_value = mock_pagination
    mock_review_repo.get_all_course_reviews.return_value = []
    mock_review_repo.get_latest_review_by_user.return_value = None
    
    response = client.get('/courses/1/reviews?sort=positive')
    assert response.status_code == 200
    mock_review_repo.get_pagination_info.assert_called_with(1, sort_order='positive', per_page=5)


def test_course_reviews_page_invalid_sort(client, mocker, sample_course):
    mock_course_repo = mocker.patch('app.courses.course_repository')
    mock_review_repo = mocker.patch('app.courses.review_repository')
    
    mock_course_repo.get_course_by_id.return_value = sample_course
    mock_pagination = mocker.MagicMock()
    mock_pagination.items = []
    mock_review_repo.get_pagination_info.return_value = mock_pagination
    mock_review_repo.get_all_course_reviews.return_value = []
    mock_review_repo.get_latest_review_by_user.return_value = None
    
    response = client.get('/courses/1/reviews?sort=invalid')
    assert response.status_code == 200
    mock_review_repo.get_pagination_info.assert_called_with(1, sort_order='newest', per_page=5)


def test_course_reviews_nonexistent_course(client, mocker):
    mock_course_repo = mocker.patch('app.courses.course_repository')
    mock_course_repo.get_course_by_id.return_value = None
    
    response = client.get('/courses/999/reviews')
    assert response.status_code == 404



def test_add_review_requires_login(client):
    response = client.post('/courses/1/add_review')
    assert response.status_code == 302


def test_add_review_success(client):
    response = client.post('/courses/1/add_review', data={
        'rating': '5',
        'text': 'Отличный курс!'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_review_repository_get_course_page_reviews(mocker, sample_review):
    mock_db = mocker.MagicMock()
    mock_db.session.execute.return_value.scalars.return_value = [sample_review]
    
    review_repo = ReviewRepository(mock_db)
    result = review_repo.get_course_page_reviews(1)
    
    mock_db.session.execute.assert_called_once()


def test_review_repository_get_latest_review_by_user(mocker, sample_review, sample_user):
    mock_db = mocker.MagicMock()
    mock_db.session.execute.return_value.scalar_one_or_none.return_value = sample_review
    
    review_repo = ReviewRepository(mock_db)
    result = review_repo.get_latest_review_by_user(1, sample_user)
    
    mock_db.session.execute.assert_called_once()
    assert result == sample_review


def test_review_repository_create_review(mocker, sample_user):
    mock_db = mocker.MagicMock()
    mock_course_repo = mocker.patch('app.repositories.review_repository.course_repository')
    
    review_repo = ReviewRepository(mock_db)
    result = review_repo.create(5, 'Отличный курс!', 1, sample_user)
    
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()
    mock_course_repo.rate_course.assert_called_once_with(1, 5)
    assert result.rating == 5
    assert result.text == 'Отличный курс!'


def test_review_repository_get_pagination_info(mocker):
    mock_db = mocker.MagicMock()
    mock_pagination = mocker.MagicMock()
    mock_db.paginate.return_value = mock_pagination
    
    review_repo = ReviewRepository(mock_db)
    result = review_repo.get_pagination_info(1, sort_order='newest', per_page=10)
    
    mock_db.paginate.assert_called_once()
    assert result == mock_pagination


def test_review_model_creation():
    review = Review(
        rating=5,
        text='Отличный курс!',
        course_id=1,
        user_id=1
    )
    
    assert review.rating == 5
    assert review.text == 'Отличный курс!'
    assert review.course_id == 1
    assert review.user_id == 1


def test_course_rating_calculation():
    course = Course(
        name='Test Course',
        short_desc='Test',
        full_desc='Test Description',
        rating_sum=15,
        rating_num=3,
        category_id=1,
        author_id=1
    )
    
    assert course.rating == 5.0


def test_course_rate_method():
    course = Course(
        name='Test Course',
        short_desc='Test',
        full_desc='Test Description',
        rating_sum=0,
        rating_num=0,
        category_id=1,
        author_id=1
    )
    
    course.rate(5)
    assert course.rating_sum == 5
    assert course.rating_num == 1
    assert course.rating == 5.0



def test_review_sorting_newest(mocker):
    mock_db = mocker.MagicMock()
    mock_query = mocker.MagicMock()
    mock_db.select.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    review_repo = ReviewRepository(mock_db)
    review_repo._all_query(1, sort_order='newest')
    
    mock_query.order_by.assert_called()


def test_review_sorting_positive(mocker):
    mock_db = mocker.MagicMock()
    mock_query = mocker.MagicMock()
    mock_db.select.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    review_repo = ReviewRepository(mock_db)
    review_repo._all_query(1, sort_order='positive')
    
    mock_query.order_by.assert_called()


def test_review_sorting_negative(mocker):
    mock_db = mocker.MagicMock()
    mock_query = mocker.MagicMock()
    mock_db.select.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.limit.return_value = mock_query
    
    review_repo = ReviewRepository(mock_db)
    review_repo._all_query(1, sort_order='negative')
    
    mock_query.order_by.assert_called()



def test_full_review_workflow(app, client):
    with app.app_context():
        category = Category(name='Test Category')
        db.session.add(category)
        db.session.commit()
        
        user = User(
            login='testuser',
            first_name='Test',
            last_name='User',
            password_hash='test_hash'
        )
        db.session.add(user)
        db.session.commit()
        
        image = Image(
            id='test-image-id',
            file_name='test.jpg',
            mime_type='image/jpeg',
            md5_hash='test-hash'
        )
        db.session.add(image)
        db.session.commit()
        
        course = Course(
            name='Test Course',
            short_desc='Short description',
            full_desc='Full description',
            category_id=category.id,
            author_id=user.id,
            rating_sum=0,
            rating_num=0,
            background_image_id='test-image-id'
        )
        db.session.add(course)
        db.session.commit()
        
        response = client.get(f'/courses/{course.id}')
        assert response.status_code == 200
        
        response = client.post(f'/courses/{course.id}/add_review', data={
            'rating': '5',
            'text': 'Отличный курс!'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        response = client.get(f'/courses/{course.id}/reviews')
        assert response.status_code == 200