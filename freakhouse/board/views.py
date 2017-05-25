from django.views.generic import ListView, DetailView
from braces.views import PrefetchRelatedMixin

from .models import Section, Thread, Post


class SectionListView(ListView):
    model = Section


class SectionDetailView(PrefetchRelatedMixin, DetailView):
    model = Section
    prefetch_related = ["threads", "threads__posts"]


class ThreadDetailView(PrefetchRelatedMixin, DetailView):
    model = Thread
    prefetch_related = ["posts"]

    def get_queryset(self):
        post = Post.objects.get(pid=self.kwargs.get('op_pid'), slug=self.slug_url_kwarg)
        return post.thread

