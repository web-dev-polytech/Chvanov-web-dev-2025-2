from ..models import db, Review
from .course_repository import CourseRepository

course_repository = CourseRepository(db)

class ReviewRepository:
    def __init__(self, db):
        self.db = db

    def _all_query(self, course_id, sort_order='newest', count=None, **kwargs):
        query = (
            self.db.select(Review)
            .filter_by(course_id=course_id)
            .filter_by(**kwargs)
        )
        
        if sort_order == 'newest':
            query = query.order_by(Review.created_at.desc())
        elif sort_order == 'positive':
            query = query.order_by(Review.rating.desc(), Review.created_at.desc())
        elif sort_order == 'negative':
            query = query.order_by(Review.rating.asc(), Review.created_at.desc())
        
        if count:
            query = query.limit(count)
        return query

    def get_pagination_info(self, course_id, sort_order='newest', per_page=5):
        query = self._all_query(course_id, sort_order=sort_order)
        return self.db.paginate(query, per_page=per_page)

    def get_all_course_reviews(self, course_id, sort_order='newest', pagination=None):
        if pagination is not None:
            return pagination.items
        return self.db.session.execute(self._all_query(course_id, sort_order=sort_order)).scalars()

    def get_course_page_reviews(self, course_id, count=5):
        return self.db.session.execute(self._all_query(course_id, sort_order='newest', count=count)).scalars()

    def get_latest_review_by_user(self, course_id, user):
        user_id = getattr(user, "id", None)
        return self.db.session.execute(self._all_query(course_id, sort_order='newest', count=1, user_id=user_id)).scalar_one_or_none()

    def create(self, rating, text, course_id, user):
        user_id = getattr(user, "id", None)
        review = Review(
            rating=rating,
            text=text,
            course_id=course_id,
            user_id=user_id
        )
        try:
            self.db.session.add(review)
            self.db.session.commit()
        except Exception as e:
            self.db.session.rollback()
            raise e
        course_repository.rate_course(course_id, rating)
        
        return review
