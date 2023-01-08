from api.views import (RecipesViewSet, IngredientsViewSet, TagsViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter
#from users.views import UserViewSet


app_name = 'api'

router = DefaultRouter()
#router.register('users', UserViewSet)
router.register('tags', TagsViewSet, basename='tags')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipesViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
]
