"""钉钉发送消息（基础通用层 · 网络与服务调用）。

抽自 sendInfobyDing.py（get_access_token/getAllinfos/send_to_user/DingTalkMessageSender），
逻辑不变；改动：应用凭据（client_id/secret/robot_code）不再硬编码，改为
参数 > 环境变量（DINGTALK_CLIENT_ID/DINGTALK_CLIENT_SECRET/DINGTALK_ROBOT_CODE）> email_config.json 的 dingtalk 段。

依赖：alibabacloud_dingtalk 系列 SDK（惰性导入，未装也能 import 本模块，仅调用时才需要）、requests。
"""
import json
import os

# 本模块在 scripts/reusable/foundation/dingtalk/ 下，email_config.json 在 scripts/（上溯三级）
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def _ding_cfg():
    """读 email_config.json 的 dingtalk 段；读不到返回 {}。"""
    try:
        with open(os.path.join(_SCRIPTS_DIR, "email_config.json"), encoding="utf-8") as f:
            return json.load(f).get("dingtalk") or {}
    except Exception:
        return {}


def resolve_creds(client_id=None, client_secret=None, robot_code=None):
    """凭据：参数 > 环境变量 > 配置。返回 (client_id, client_secret, robot_code)。"""
    cfg = _ding_cfg()
    cid = client_id or os.environ.get("DINGTALK_CLIENT_ID") or cfg.get("client_id")
    csec = client_secret or os.environ.get("DINGTALK_CLIENT_SECRET") or cfg.get("client_secret")
    rc = robot_code or os.environ.get("DINGTALK_ROBOT_CODE") or cfg.get("robot_code") or cid
    return cid, csec, rc


def get_access_token(client_id=None, client_secret=None):
    """用应用凭据换 access_token；失败返回 None。凭据不给则走环境变量/配置。"""
    from alibabacloud_dingtalk.oauth2_1_0.client import Client as DingTalkOAuthClient
    from alibabacloud_dingtalk.oauth2_1_0 import models as oauth_models
    from alibabacloud_tea_openapi import models as open_api_models
    cid, csec, _ = resolve_creds(client_id, client_secret)
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    client = DingTalkOAuthClient(config)
    request = oauth_models.GetAccessTokenRequest(app_key=cid, app_secret=csec)
    try:
        response = client.get_access_token(request)
        return getattr(response.body, "access_token", None)
    except Exception as e:
        print("获取 access_token 失败:", e)
        return None


def get_users(access_token):
    """列通讯录，返回 {姓名: userId}（翻页取全）。"""
    import requests
    data = {"cursor": 0, "contain_access_limit": 'true', "size": 100,
            "order_field": "entry_asc", "language": "zh_CN", "dept_id": "1"}
    url = f"https://oapi.dingtalk.com/topapi/user/listsimple?access_token={access_token}"
    resp = json.loads(requests.post(url, data=data).text)
    users = {u['name']: str(u['userid']) for u in resp['result']['list']}
    while resp['result']['has_more']:
        data['cursor'] += 100
        resp = json.loads(requests.post(url, data=data).text)
        users.update({u['name']: str(u['userid']) for u in resp['result']['list']})
    return users


def send_to_user(robot_code, access_token, user_id, content):
    """给指定 userId 发一条文本消息（OTO 主动推送）。返回 API 响应。"""
    from alibabacloud_dingtalk.robot_1_0.client import Client as RobotClient
    from alibabacloud_dingtalk.robot_1_0 import models as robot_models
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_tea_util import models as util_models
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    client = RobotClient(config)
    headers = robot_models.BatchSendOTOHeaders()
    headers.x_acs_dingtalk_access_token = access_token
    request = robot_models.BatchSendOTORequest(
        robot_code=robot_code, user_ids=[user_id], msg_key='sampleText',
        msg_param=json.dumps({"content": content}, ensure_ascii=False))
    return client.batch_send_otowith_options(request, headers, util_models.RuntimeOptions())


def send_message(name, content, client_id=None, client_secret=None, robot_code=None):
    """按姓名给某人发文本消息（一站式：换 token → 查 userId → 发送）。凭据走参数/环境变量/配置。

    输入：name 目标姓名；content 文本；凭据可选
    输出：API 响应；取不到 token/userId 时返回 None
    """
    cid, csec, rc = resolve_creds(client_id, client_secret, robot_code)
    token = get_access_token(cid, csec)
    if not token:
        return None
    uid = (get_users(token) or {}).get(name)
    if not uid:
        print(f"[dingtalk] 未在通讯录找到用户: {name}")
        return None
    return send_to_user(rc, token, uid, content)
