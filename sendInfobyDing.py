from alibabacloud_dingtalk.robot_1_0.client import Client as RobotClient
from alibabacloud_dingtalk.robot_1_0 import models as robot_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_dingtalk.oauth2_1_0.client import Client as DingTalkOAuthClient
from alibabacloud_dingtalk.oauth2_1_0 import models as oauth_models
import requests,json



def get_access_token(client_id, client_secret):
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    client = DingTalkOAuthClient(config)

    request = oauth_models.GetAccessTokenRequest(
        app_key=client_id,
        app_secret=client_secret
    )

    try:
        response = client.get_access_token(request)
        token = getattr(response.body, "access_token", None)
        expire_in = getattr(response.body, "expire_in", 7200)
        print("access_token:", token)
        print("有效期:", expire_in, "秒")
        return token
    except Exception as e:
        print("获取 access_token 失败:", e)
        return None
def send_to_user(robot_code, access_token, user_id, content):
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    client = RobotClient(config)

    headers = robot_models.BatchSendOTOHeaders()
    headers.x_acs_dingtalk_access_token = access_token

    request = robot_models.BatchSendOTORequest(
        robot_code=robot_code,
        user_ids=[user_id],       # 指定用户
        msg_key='sampleText',     # 文本消息类型
        msg_param=f'{{"content":"{content}"}}'
    )

    response = client.batch_send_otowith_options(
        request,
        headers,
        util_models.RuntimeOptions()
    )
    return response
def getAllinfos(access_token):
    print('ding get info....')
    data = {
        "cursor": 0,
        "contain_access_limit": 'true',
        "size": 100,
        "order_field": "entry_asc",
        "language": "zh_CN",
        "dept_id": "1"
    }
    response = requests.post(f"https://oapi.dingtalk.com/topapi/user/listsimple?access_token={access_token}",data=data)
    allinfos = json.loads(response.text)
    users = {u['name']:str(u['userid']) for u in allinfos['result']['list']}
    while allinfos['result']['has_more']:
        data['cursor'] += 100
        response = requests.post(f"https://oapi.dingtalk.com/topapi/user/listsimple?access_token={access_token}",data=data)
        allinfos = json.loads(response.text)
        users_t = {u['name']:str(u['userid']) for u in allinfos['result']['list']}
        users.update(users_t)
    return users


class DingTalkMessageSender:
    """钉钉消息发送类，封装发送消息的完整流程"""
    def __init__(self):
        # 固定参数
        self.robot_code = "dingm46gn6df3kr3pfgv"
        self.client_id = "dingm46gn6df3kr3pfgv"
        self.client_secret = "1MCXVX_iIboVcXr9hgi5Ue9JudYR8PDsTzcNsRw02DH88O39XwUMFcaSOb1lY3oI"
    
    def send_message(self, dName, msg):
        """
        发送消息到指定用户
        
        Args:
            dName: 目标用户姓名（变量）
            msg: 要发送的消息内容（变量）
        
        Returns:
            发送响应结果
        """
        access_token = get_access_token(self.client_id, self.client_secret)
        user_id = getAllinfos(access_token)[dName]
        return send_to_user(
            robot_code=self.robot_code,
            access_token=access_token,
            user_id=user_id,  # 目标用户的 staffId
            content=msg
        )


# 使用示例
if __name__ == "__main__":
    sender = DingTalkMessageSender()
    sender.send_message(dName='毕海灵', msg='当下做到哪一步了')
