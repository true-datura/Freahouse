from datetime import datetime
from random import randint
from time import time

from django.db import models
from django.core.urlresolvers import reverse


def files_resolver(instance, filename):
    return "section/{timestamp}{salt}.{ext}".format(
        timestamp=int(time() * 100),
        salt=randint(10, 99), ext=instance.type.extension
    )


def thumbs_resolver(instance, filename):
    return "thumbs/{timestamp}{salt}.{ext}".format(
        timestamp=int(time() * 100),
        salt=randint(10, 99), ext=instance.type.extension
    )


class FileType(models.Model):
    """File type"""
    extension = models.CharField("Extension", max_length=10)
    mime = models.CharField("MIME", max_length=250)

    def __str__(self):
        return self.extension


class File(models.Model):
    """Represents files at the board."""
    name = models.CharField("Original name", max_length=64)
    type = models.ForeignKey(FileType)
    is_deleted = models.BooleanField("Is deleted", default=False)
    hash = models.CharField("Hash", max_length=32, blank=True)
    file = models.FileField("Location", upload_to=files_resolver)
    thumb = models.ImageField("Thumbnail", upload_to=thumbs_resolver)
    image_width = models.PositiveSmallIntegerField("Image width", blank=True)
    image_height = models.PositiveSmallIntegerField("Image height", blank=True)

    @property
    def post(self):
        return self.post_set.get()

    def __str__(self):
        return self.hash


class Section(models.Model):
    """Board section."""
    slug = models.SlugField("Slug", max_length=5, unique=True)
    name = models.CharField("Name", max_length=64)
    description = models.TextField("Description", blank=True)
    file_types = models.ManyToManyField(FileType)
    force_files = models.BooleanField(
        "Force to post file on thread creation", default=True
    )
    filesize_limit = models.PositiveIntegerField(
        "Filesize limit", default=2 ** 20 * 10  # Mbytes
    )
    anonymity = models.BooleanField("Force anonymity", default=False)
    default_name = models.CharField(
        "Default poster name", max_length=64, default="Anonymous"
    )
    bumplimit = models.PositiveSmallIntegerField(
        "Max posts in thread", default=500
    )
    threadlimit = models.PositiveSmallIntegerField("Max threads", default=200)
    threads_per_page = models.PositiveSmallIntegerField(
        "Max threads on page", default=20
    )

    def threads(self):
        return Thread.objects.filter(section=self.id).order_by("-bump", "-id")

    def op_posts(self):
        """List of first posts in section."""
        return Post.objects.filter(
            is_op_post=True,
            thread__section=self.id
        ).order_by("-date", "-pid")

    def posts(self):
        """List of posts in section."""
        return Post.objects.filter(thread__section=self.id).order_by(
            "-date", "-pid")

    def files(self):
        """List of files in section."""
        return File.objects.filter(post__thread__section=self.id)

    def allowed_filetypes(self):
        """List of allowed MIME types of section."""
        return self.file_types.values_list("mime", "extension")

    def __str__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('section_detail', kwargs={'slug': self.slug})


class Thread(models.Model):
    """Groups of posts."""
    bump = models.DateTimeField("Bump", blank=True, db_index=True)
    section = models.ForeignKey(Section, related_name='threads')

    class Meta:
        get_latest_by = "bump"
        ordering = ["-bump"]

    def thread_info(self, limit=5):
        """Returns dict, that contains info about thread files and posts."""
        total = self.posts.count()
        if total <= limit:
            return {"total": total, "skipped": 0, "skipped_files": 0}
        start = total - limit
        return {
            "total": total,
            "start": start,
            "stop": total,
            "skipped": start - 1,
        }

    @property
    def op_post(self):
        return self.posts.first()

    def last_posts(self):
        thread_info = self.thread_info()
        posts = self.posts.all()
        if not thread_info["skipped"]:
            return posts
        # select first and last 5 posts
        start, stop = thread_info["start"], thread_info["stop"]
        return [posts[0]] + list(posts[start:stop])

    def get_absolute_url(self):
        return reverse('thread_detail', kwargs={'slug': self.slug})


class Post(models.Model):
    """Represents post."""
    pid = models.PositiveIntegerField("PID", blank=True, db_index=True)
    thread = models.ForeignKey(Thread, blank=True, null=True, related_name='posts')
    op_post = models.BooleanField("First post in thread", default=False)
    date = models.DateTimeField("Bump", default=datetime.now, blank=True)
    poster = models.CharField("Name", max_length=32, blank=True, null=True)
    tripcode = models.CharField("Tripcode", max_length=32, blank=True)
    email = models.CharField("Email", max_length=32, blank=True)
    topic = models.CharField("Topic", max_length=48, blank=True)
    file = models.OneToOneField(File, blank=True, null=True)
    password = models.CharField("Password", max_length=64, blank=True)
    message = models.TextField("Message", blank=True)
    message_html = models.TextField(blank=True)

    class Meta:
        get_latest_by = "pid"
        ordering = ["pid"]

    def section(self):
        return self.thread.section

    def section_slug(self):
        return self.thread.section.slug

    def __str__(self):
        if self.op_post:
            return 'Thread № {}'.format(self.pid)
        return 'Post № {}'.format(self.pid)
