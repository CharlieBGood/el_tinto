from rest_framework.routers import DefaultRouter

from el_tinto.users.views import RegisterViewset

register_router = DefaultRouter()

register_router.register(r'register', RegisterViewset, basename='register')

urlpatterns = register_router.urls
