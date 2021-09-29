from django.urls import path, include

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),
    path('add/', views.addFile, name='addFile'),
    path(r'files/<path:filePath>', views.showFile, name='showFile'),
    path('addD/', views.addDirectory, name='addDirectory'),
    path('addedDir/', views.addedDirectory, name='addedDirectory'),
    path('addedFile/', views.addedFile, name='addedFile'),
    path('delete/', views.delete, name='delete'),
    path('deleteDone/', views.deleteDone, name='deleteDone'),
    path('provers', views.provers, name='provers'),
    path('verification', views.verification, name='verification'),
    path('result/', views.result, name='result'),
    path('rerun/', views.rerun, name='rerun'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]