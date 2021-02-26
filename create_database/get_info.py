from create_database import configs
import time
from pixivpy3 import PixivAPI

_REQUESTS_KWARGS = {
    'proxies': {
        'https': configs.proxy,
    },
    'verify': True,  # PAPI use https, an easy way is disable requests SSL verify
}

start_time = time.time()
api = PixivAPI(**_REQUESTS_KWARGS)
api.set_auth(configs.pixiv.access_token, configs.pixiv.refresh_token)
# api.login(configs.pixiv.user, configs.pixiv.passwd)
# json_result = api.illust_detail(59580629)
# illust = json_result.illust
# print(">>> origin url: %s" % illust.image_urls['large'])
# api.auth(configs.pixiv.user, configs.pixiv.passwd, configs.pixiv.refresh_token)
json_result = api.works(46363414)
print(json_result)
illust = json_result.response[0]
print(">>> %s, origin url: %s" % (illust.caption, illust.image_urls['large']))

end_time = time.time()
print(end_time - start_time, 's')
