from django.urls import path

from . import views

urlpatterns = [
    # Ro'yxatlar
    path('tamirlar/', views.tamir_royxati, name='tamir_royxati'),
    path('murojaatlar/', views.murojaatlar_navbati, name='murojaatlar_navbati'),
    path('navbat/', views.navbat, name='navbat'),
    path('tasdiqlash/', views.tasdiqlash_navbati, name='tasdiqlash_navbati'),

    # Yangi yozuvlar
    path('murojaat/yangi/', views.murojaat_yangi, name='murojaat_yangi'),
    path('murojaat/operator/', views.operator_murojaat, name='operator_murojaat'),
    path('murojaat/ozim/', views.ozi_tamir_yangi, name='ozi_tamir_yangi'),

    # Bitta ta'mir
    path('tamirlar/<int:pk>/', views.tamir_batafsil, name='tamir_batafsil'),
    path('tamirlar/<int:pk>/qabul/', views.murojaat_qabul, name='murojaat_qabul'),
    path('tamirlar/<int:pk>/rad/', views.murojaat_rad, name='murojaat_rad'),
    path('tamirlar/<int:pk>/biriktirish/', views.usta_biriktirish, name='usta_biriktirish'),
    path('tamirlar/<int:pk>/olish/', views.ishni_olish, name='ishni_olish'),
    path('tamirlar/<int:pk>/soralganni-rad/', views.soralganni_rad, name='soralganni_rad'),
    path('tamirlar/<int:pk>/boshlash/', views.ishni_boshlash, name='ishni_boshlash'),
    path('tamirlar/<int:pk>/yakunlash/', views.ishni_yakunlash, name='ishni_yakunlash'),
    path('tamirlar/<int:pk>/topshirish/', views.topshirish, name='topshirish'),
    path('tamirlar/<int:pk>/baho/', views.baho_berish, name='baho_berish'),
    path('tamirlar/<int:pk>/tasdiq/', views.tasdiq_qarori, name='tasdiq_qarori'),
]
