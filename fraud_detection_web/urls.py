"""
URL configuration for fraud_detection_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from fraud_detection import auth_views as custom_auth_views
from fraud_detection import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', custom_auth_views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', custom_auth_views.logout_view, name='logout'),
    path('register/', custom_auth_views.register, name='register'),
    path('pending-approval/', custom_auth_views.pending_approval, name='pending_approval'),
    path('user-approval-list/', custom_auth_views.user_approval_list, name='user_approval_list'),
    path('toggle-model-status/<int:model_id>/', views.toggle_model_status, name='toggle_model_status'),
    path('approve-user/<int:user_id>/', custom_auth_views.approve_user, name='approve_user'),
    path('predict/', views.predict, name='predict'),
    path('train-model/', views.train_model, name='train_model'),
    path('model-comparison/', views.model_comparison, name='model_comparison'),
    path('user-management/', custom_auth_views.user_approval_list, name='user_management'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
