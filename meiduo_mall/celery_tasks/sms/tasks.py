from celery_tasks.main import celery_app
from celery_tasks.sms.yuntongxun.sms import CCP


@celery_app.task(name="send_sms_code")
def ccp_send_sms_code(mobile,sms_code):

    CCP().send_template_sms(mobile,[sms_code, 5], 996)


# # 编写异步任务代码
# from celery_tasks.sms.yuntongxun.sms import CCP
# from celery_tasks.main import celery_app
#
# @celery_app.task(name='send_sms_code')  # 此装饰器作为是让下面的函数真正的成功celery的任务
# def send_sms_code(mobile, sms_code):
#     """
#     利用celery异步发送短信
#     :param mobile: 要收到短信的手机号
#     :param sms_code: 短信验证码
#     """
#     CCP().send_template_sms(mobile, [sms_code,  5], 1)
