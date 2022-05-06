from django.urls import path

from .views      import LikeView, ProductDetailView, ProductListView, ProductSearchView, ProductRecommendView

urlpatterns = [
	path('/detail/<str:sku_number>', ProductDetailView.as_view()),
	path('/like/<int:product_id>', LikeView.as_view()),
	path('/list', ProductListView.as_view()),
	path('/search', ProductSearchView.as_view()),
	path('/recommend', ProductRecommendView.as_view()),
]
