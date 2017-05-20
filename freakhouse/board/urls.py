from django.conf.urls import url

from .views import SectionListView

urlpatterns = [
    url(r'^$', SectionListView.as_view()),
]
