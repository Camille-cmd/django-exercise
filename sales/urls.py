from django.urls import include, path
from rest_framework import routers
from sales.views import ArticleCreateView, SaleView, SaleDetailView, SalesByArticleListView

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('article/', ArticleCreateView.as_view()),
    path('sale/', SaleView.as_view()),
    path('sale/<str:pk>', SaleDetailView.as_view()),
    path('sale_by_article', SalesByArticleListView.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
