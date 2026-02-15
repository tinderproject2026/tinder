from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login, name='auth'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path("dating/", views.dating, name="dating"),

    path("like/<int:user_id>/", views.like_user),
    path("dislike/<int:user_id>/", views.dislike_user),

    path("likes/", views.likes),

    path("accept/<int:user_id>/", views.accept_like),
    path("reject/<int:user_id>/", views.reject_like),

    path("dating/", views.dating, name="dating"),
    path("like/<int:user_id>/", views.like_user, name="like"),
    path("dislike/<int:user_id>/", views.dislike_user, name="dislike"),
    path("likes/", views.likes, name="likes"),
    path("sympathy/", views.sympathy, name="sympathy"),

]

urlpatterns += static('/images/', document_root='images')
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
