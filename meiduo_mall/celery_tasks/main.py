from celery import Celery
import os

# 告诉celery 它里面需要用的django配置文件在那里
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

celery_app = Celery("meiduo_mall")
# 加载配置

celery_app.config_from_object("celery_tasks.config")

celery_app.autodiscover_tasks(['celery_tasks.sms', "celery_tasks.emails"])
