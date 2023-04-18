from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import force_authenticate, APIRequestFactory

from sales.models import Sale, Article, ArticleCategory
from sales.views import SalesByArticleListView
from users.models import User


class SalesTest(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(email="test@example.com", password="test")
        self.category = ArticleCategory.objects.create(display_name="Category_test")
        self.article1 = Article.objects.create(
            code="ABC123", category=self.category, name="ArticleTest1", manufacturing_cost="100"
        )
        self.article2 = Article.objects.create(
            code="ABC456", category=self.category, name="ArticleTest2", manufacturing_cost="50"
        )

        for i in range(0, 10):
            date = timezone.now() - timezone.timedelta(days=i)
            Sale.objects.create(
                date=date, author=self.user, article=self.article1, quantity=1, unit_selling_price=110
            )

        for i in range(0, 10):
            date = timezone.now() - timezone.timedelta(days=i)
            Sale.objects.create(
                date=date, author=self.user, article=self.article2, quantity=i, unit_selling_price=100
            )

    def test_sales_by_article_list(self):
        """Test that we get sales by article in the correct order"""
        factory = APIRequestFactory()
        view = SalesByArticleListView.as_view()

        request = factory.get('/accounts/django-superstars/')
        force_authenticate(request, user=self.user)
        response = view(request)

        # ArticleTest2 is in first as the total sell price is the highest
        expected_data = {
            'ArticleTest2': {
                'category': 'Category_test',
                'last_sale': timezone.now().date(),
                'net_margin': Decimal('2250.00'),
                'total_sell_price': Decimal('4500.00')
            },
            'ArticleTest1': {
                'category': 'Category_test',
                'last_sale': timezone.now().date(),
                'net_margin': Decimal('100.00'),
                'total_sell_price': Decimal('1100.00')
            }
        }
        self.assertEqual(response.data, expected_data)
