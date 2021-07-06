from django.urls import path, re_path, include

urlpatterns = [
    path('api/', include('app.api.urls')),
]