from django.urls import path

from . import views

urlpatterns = [
    path('hisobotlar/', views.hisobot, name='hisobot'),
    path('hisobotlar/excel/', views.hisobot_excel, name='hisobot_excel'),
    path('hisobotlar/pdf/', views.hisobot_pdf, name='hisobot_pdf'),
]
