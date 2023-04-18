from django.db.models import Sum, F, Count
from django.utils import timezone
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from sales.models import Article, Sale
from sales.permissions import IsOwnerOnly
from sales.serializers import ArticleSerializer, SaleSerializer


class ArticleCreateView(generics.CreateAPIView):
    """View to create a new article"""
    queryset = Article.objects.all().order_by("code")
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]


class SaleView(generics.ListCreateAPIView):
    """View to create Sale"""
    queryset = Sale.objects.all().order_by("-date")
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Add author and date automatically
            serializer.validated_data['date'] = timezone.now()
            serializer.validated_data['author'] = request.user
            serializer.save()
            return Response({"status": "success", "sale": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SaleDetailView(generics.GenericAPIView):
    """Detail view for a sale to be able to update and delete it only for the original author"""
    queryset = Sale.objects.all().order_by("-date")
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOnly]

    def patch(self, request, *args, **kwargs):
        sale = self.get_object()
        serializer = self.serializer_class(sale, data=request.data, partial=True)
        if serializer.is_valid():
            # Add author and date automatically
            serializer.validated_data['date'] = timezone.now()
            serializer.validated_data['author'] = request.user
            serializer.save()
            return Response({"status": "success", "sale": serializer.data})
        return Response({"status": "fail", "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        sale = self.get_object()
        sale.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesByArticleListView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SaleSerializer

    def get_queryset(self, *args, **kwargs):
        """Get the Sales' article with the total of their sales and net margin"""
        return Sale.objects.prefetch_related(
            "article", "article__category"
        ).values("article").annotate(
            total_sell_price=Sum(F('quantity') * F('unit_selling_price')),
            net_margin=Sum((F('unit_selling_price') - F('article__manufacturing_cost')) * F('quantity'))
        ).order_by("-total_sell_price")

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = dict()
        for article_data in queryset:
            article = Article.objects.get(pk=article_data["article"])
            data[article.name] = {
                "category": article.category.display_name,
                "last_sale": article.sales.order_by("date").last().date,
                "net_margin": round(article_data["net_margin"], 2),
                "total_sell_price": round(article_data["total_sell_price"], 2),
            }
        return Response(data)
