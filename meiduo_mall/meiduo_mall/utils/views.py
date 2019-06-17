from django.contrib.auth import mixins
from django.views import View


class Lr(mixins.LoginRequiredMixin, View):
    pass