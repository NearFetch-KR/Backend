from django.urls import path

from .views      import LikeView, ProductDetailView, ProductListView, ProductSearchView, MainHotItemView, MainRecommendView, MakeCategoryView, MakeFilterView, MakeBrandListView

urlpatterns = [
	path('/detail/<str:sku_number>', ProductDetailView.as_view()),
	path('/like/<int:product_id>', LikeView.as_view()),
	path('/list', ProductListView.as_view()),
	path('/search', ProductSearchView.as_view()),
	path('/main/recommend', MainRecommendView.as_view()),
	path('/main/hotitem', MainHotItemView.as_view()),
	path('/make/category', MakeCategoryView.as_view()),
	path('/make/filter', MakeFilterView.as_view()),
	path('/make/brand/list', MakeBrandListView.as_view()),
]
