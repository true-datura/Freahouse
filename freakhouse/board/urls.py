from django.conf.urls import url

from .views import SectionListView, SectionDetailView, ThreadDetailView

urlpatterns = [
    url(r'^$', SectionListView.as_view(), name='section_list'),
    url(r'^(?P<slug>[-\w]+)/$', SectionDetailView.as_view(), name='section_detail'),
    url(r'^(?P<slug>[-\w]+)/(?P<op_pid>\d+)$', ThreadDetailView.as_view(), name='thread_detail'),
]
