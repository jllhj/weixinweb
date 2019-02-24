data_dict = {
    'k1':'v1',
    'k2':'垃圾'
}

import json
rsult = json.dumps(data_dict,ensure_ascii=False)
print(rsult)
"""
# 示例一：
requests.post(
    url=msg_url,
    json={
    'k1':'v1',
    'k2':'垃圾'
    }
    )


# 示例二：
    requests.post(
    url=msg_url,
    data=bytes(json.dumps({
    'k1':'v1',
    'k2':'垃圾'
    },ensure_ascii=False),encoding='utf-8)
    )
    
    
"""
