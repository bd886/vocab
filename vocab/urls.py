from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_vocab, name='add_vocab'),
    path('add_category/', views.add_category, name='add_category'),
    path('learn/', views.learn_vocab, name='learn_vocab'),
    path('test/', views.test_vocab, name='test_vocab'),
    path('start_test/', views.start_test, name='start_test'),
    path('run_test/', views.run_test, name='run_test'),
    path('test_summary/<int:test_id>/', views.test_summary, name='test_summary'),
    path('test_overview/', views.test_overview, name='test_overview'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]