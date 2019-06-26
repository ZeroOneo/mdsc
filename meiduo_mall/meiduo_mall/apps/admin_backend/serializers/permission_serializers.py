from rest_framework import serializers,

from django.contrib.auth.models import Permission

class PermissionSerializers(serializers.ModelSerializer):



    class Meta:

        model = Permission

        fields ="__all__"
    #
    # name = models.CharField(_('name'), max_length=255)
    # content_type = models.ForeignKey(
    #     ContentType,
    #     models.CASCADE,
    #     verbose_name=_('content type'),
    # )
    # codename = models.CharField(_('codename'), max_length=100)
    # objects = PermissionManager()

# "id": "权限id",
# "name": "权限名称",
# "codename": "权限识别名",
# "content_type": "权限类型"