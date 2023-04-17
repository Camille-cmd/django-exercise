from django.contrib import admin

from sales.models import Sale, Article


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    pass

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    pass

