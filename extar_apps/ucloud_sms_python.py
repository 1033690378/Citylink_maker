from ucloud.core import exc
from ucloud.client import Client


def send_sms(mobile, code):
    client = Client({
        "public_key": "1p5EQMHrZYL7o70jkLT2FY2qRS4zbk3LK8MKbuhEP",
        "private_key": "7CpeYlJRMVSEXkfXBlIVG3cBsrDochG87HkzmqFauN3yNhuJdJCUFfyHS8r8DLG",
        "project_id": "org-gytmoe",
    })

    try:
        resp = client.usms().send_usms_message({
            'PhoneNumbers': [mobile],  # 手机号列表（PhoneNumbers）
            'SigContent': "legendweb",  # 短信签名（SigContent）
            'TemplateId': "UTA220309181K7K",  # 短信模板 ID（TemplateId）
            'TemplateParams': [code],  # 短信模板参数列表（TemplateParams）
        })
    except exc.UCloudException as e:
        # print(e)
        return e
    else:
        # print(resp)
        return resp
