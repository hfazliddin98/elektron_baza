from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('panel/', views.dashboard, name='dashboard'),
    path('kirish/', views.KirishView.as_view(), name='login'),
    path('chiqish/', views.ChiqishView.as_view(), name='logout'),
    path('parol/', views.ParolOzgartirishView.as_view(), name='parol_ozgartirish'),
    path('parol/tayyor/', views.ParolTayyorView.as_view(), name='parol_tayyor'),
    path('amal-tarixi/', views.amal_tarixi, name='amal_tarixi'),
]
