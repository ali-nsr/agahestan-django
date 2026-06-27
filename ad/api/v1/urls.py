from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('<city>/ads/', views.AdListAPIView.as_view(), name='ad-list'),
    path('ads/<str:uuid>/', views.AdRetrieveAPIView.as_view(), name='ad-detail'),
    path('<city>/<category_slug>/', views.CategoryListAPIView.as_view(), name='category-list'),
    path('search/', views.AdSearchGetAPIView.as_view(), name='search'),
    path('search-ajax/', views.AdSearchAjaxAPIView.as_view(), name='search-ajax'),
    path('categories/', views.CategoryChoiceAPIView.as_view(), name='categories'),
    path('category/<category_slug>/fields/', views.CategoryFieldsAPIView.as_view(), name='category-fields'),

    # path('report/ad-report/create/<ad_id>/', views.AdReportAPIView.as_view(), name='ad-report'),
    # path('report/ad-report-reasons/list/', views.AdReportReasonsAPIView.as_view(), name='ad-report-reasons'),
    path('ads/<str:ad_uuid>/views/', views.AdViewsChartAPIView.as_view()),

    path('ads/<category_slug>/create/', views.AdCreateView.as_view(), name='ad-create'),
    path('ads/<int:ad_id>/update/', views.AdUpdateAPIView.as_view(), name='ad-update'),
    path('ads/<int:ad_id>/delete/', views.AdDeleteAPIView.as_view(), name='ad-delete'),
    path('ads/<int:ad_id>/create-ad-attributes/', views.AdAttributeUpdateView.as_view(), name='ad-attributes'),
    path('ads/<int:ad_id>/create-ad-gallery/', views.GalleryCreateView.as_view(), name='ad-gallery'),

    path('ads/<gallery_id>/gallery-delete/', views.GalleryImageDeleteAPIView.as_view(), name='ad-delete'),

    # path('pay/ad/<str:ad_uuid>/', views.PayAdPrice.as_view(), name='pay-ad-price'),
]
