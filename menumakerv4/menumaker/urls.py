"""menumaker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from menumakerapp import views
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.welcome),
    path('cuisines/', views.list_cuisines),
    path('cartadd/<int:id>/<str:role>/', views.cartadd, name='cartadd'),
    path('signup/', views.signup),
    path('my_page/', views.my_page),
    path('login/', views.login_call),
    path('logout/', views.logout_call),
    path('pdf/', views.GeneratePdf.as_view() , name='pdf'),
    path('downloadpdf/', views.DownloadPdf.as_view()),
    path('GeneratePdf/', views.GeneratePdf.as_view()),

    path('email/', views.send_email),
    path('cadmin/', views.cadmin),
    path('admin_page/', views.admin_page),
    path('add_admin/', views.add_admin),
    path('add_cuisine/', views.add_cuisine),
    path('add_cuisine_data/', views.add_cuisine_data),
    path('all_cuisine_list/', views.all_cuisine_list),

    path('logout_admin/', views.logout_admin),

    path('users_list/', views.users_list),
    path('profile/', views.profile),

    
]
