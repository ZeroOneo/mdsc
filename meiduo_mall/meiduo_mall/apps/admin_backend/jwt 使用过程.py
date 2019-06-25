import hashlib
import hmac
import json, base64

'''
jwt = base64 "header + . + payload + ." + signature

signature = hmac (header + payload)

'''

# 第一部分 ： 头部
header = {
    "typ": "JWT",  # 类型声明  JWT
    "alg": "HS256"  # 加密算法
}

# 转换成字符串
header_str = json.dumps(header)

# base64处理
header_b = base64.b64encode(header_str.encode())

print("header_b : %s" % header_b)
# 第二部分 ：载荷

"""
iss: jwt签发者
sub: jwt所面向的用户
aud: 接收jwt的一方
exp: jwt的过期时间，这个过期时间必须要大于签发时间
nbf: 定义在什么时间之前，该jwt都是不可用的.
iat: jwt的签发时间
jti: jwt的唯一身份标识，主要用来作为一次性token,从而回避重放攻击。
"""
payload = {
    "sub": "1234567890",
    "name": "John Doe",
    "admin": True
}

# 转换成字符串
payload_str = json.dumps(payload)

# base64处理
payload_b = base64.b64encode(payload_str.encode())

print("payload_b : %s" % payload_b)

# 第三部分： 签证

# 拼接加密信息
msg = header_b + b"." + payload_b

print("msg:",msg)

# 加密得到singature

SECRET_KEY = b'&$h^avul7y*i7moi^gks!sb1s8v(_&p)u5kn)*ud*4n_r8vc@g'

hobj = hmac.new(SECRET_KEY, msg, digestmod=hashlib.sha256)

signature = hobj.hexdigest()

print("signature: %s" % signature)

JWT_TOKEN = header_b.decode() + "." + payload_b.decode() + "." + signature

# header_b : b'eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJIUzI1NiJ9'
# payload_b : b'eyJzdWIiOiAiMTIzNDU2Nzg5MCIsICJuYW1lIjogIkpvaG4gRG9lIiwgImFkbWluIjogdHJ1ZX0='
# signature: d0e2ca575870c87d2fe68665d8792cb2c9a989c22719229584735d9bbae57c93


# 校验流程
# 浏览器传来JWT_TOKEN

header_str = JWT_TOKEN.split(".")[0]

payload_str = JWT_TOKEN.split(".")[1]

signature = JWT_TOKEN.split(".")[2]

signature_str = header_str + "." + payload_str
print(signature_str)
signature_new = hmac.new(SECRET_KEY, signature_str.encode(), digestmod=hashlib.sha256).hexdigest()
# new_signature = hmac.new(SECRET_KEY, new_msg.encode(), digestmod=hashlib.sha256).hexdigest()
print(signature_new)
if signature_new == signature:

    print("校验成功")

else:
    print("数据被改")
