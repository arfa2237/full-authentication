from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scheduling/', views.scheduling, name='scheduling'), 
    path('vpd/', views.vpd, name='vpd'),
    path('faq/', views.faq, name='faq'),
    path('child-vaccination/', views.child_vaccination, name='child_vaccination'),
    path('hepatitis/', views.hepatitis, name='hepatitis'),
    path('mmr/', views.mmr, name='mmr'),
    path('measles/', views.measles, name='measles'),
    path('mumps/', views.mumps, name='mumps'),
    path('rubella/', views.rubella, name='rubella'),
    path('pneumococcal/', views.pneumococcal, name='pneumococcal'),
    path('tetanus/', views.tetanus, name='tetanus'),
    path('patient/', views.patient, name='patient'),
    path('blog/1/', views.blog1, name='blog1'),
    path('blog/2/', views.blog2, name='blog2'),
    path('blog/3/', views.blog3, name='blog3'),
    path('nearby/', views.nearby, name='nearby'),
]