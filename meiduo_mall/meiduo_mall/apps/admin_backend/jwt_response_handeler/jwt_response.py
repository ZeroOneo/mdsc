def custom_jwt_response_handler(token,user=None,request=None):

    return {
        "token":token,
        "username":user.username,
        "user_id":user.id,
    }