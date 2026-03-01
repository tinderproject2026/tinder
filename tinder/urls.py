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
    path("messages/", views.chat, name="chat"),
    path("messages/<int:partner_id>/", views.chat, name="chat_with_partner"),
    path("messages/profile/<int:partner_id>/", views.chat_partner_profile, name="chat_partner_profile"),
    path("api/latest-chat/", views.latest_chat_data, name="latest_chat_data"),
    path("api/latest-chat/send/", views.latest_chat_send, name="latest_chat_send"),
    path("delete-message/<int:message_id>/", views.delete_message, name="delete_message"),

]

urlpatterns += static('/images/', document_root='images')
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
