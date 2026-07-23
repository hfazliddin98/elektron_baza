from django.urls import path

from . import views

urlpatterns = [
    # Qurilmalar
    path('qurilmalar/', views.qurilma_royxati, name='qurilma_royxati'),
    path('qurilmalar/yangi/', views.qurilma_yangi, name='qurilma_yangi'),
    path('qurilmalar/import/', views.qurilma_import, name='qurilma_import'),
    path('qurilmalar/qr-chop/', views.qr_chop, name='qr_chop'),
    path('qurilmalar/<int:pk>/', views.qurilma_batafsil, name='qurilma_batafsil'),
    path('qurilmalar/<int:pk>/tahrirlash/', views.qurilma_tahrirlash, name='qurilma_tahrirlash'),
    path('qurilmalar/<int:pk>/holat/', views.qurilma_holat, name='qurilma_holat'),
    path('qurilmalar/<int:pk>/qr.png', views.qurilma_qr, name='qurilma_qr'),

    # Bo'limlar
    path('bolimlar/', views.bolim_royxati, name='bolim_royxati'),
    path('bolimlar/yangi/', views.bolim_yangi, name='bolim_yangi'),
    path('bolimlar/<int:pk>/tahrirlash/', views.bolim_tahrirlash, name='bolim_tahrirlash'),

    # Xodimlar
    path('xodimlar/', views.xodim_royxati, name='xodim_royxati'),
    path('xodimlar/yangi/', views.xodim_yangi, name='xodim_yangi'),
    path('xodimlar/import/', views.xodim_import, name='xodim_import'),
    path('xodimlar/<int:pk>/tahrirlash/', views.xodim_tahrirlash, name='xodim_tahrirlash'),

    # Excel shablonlari
    path('shablon/<str:tur>/', views.shablon_yuklab_olish, name='shablon'),
]
