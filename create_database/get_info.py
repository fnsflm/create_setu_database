# from pixivapi import Client
from create_database import configs
import time
from pixivpy3 import PixivAPI

start_time = time.time()
# client = Client()
# client.login(configs.pixiv.user, configs.pixiv.passwd)
# illustration = client.fetch_illustration(70497369)
# print(illustration.tags)

api = PixivAPI()
api.login(configs.pixiv.user, configs.pixiv.passwd)
# json_result = api.illust_detail(59580629)
# illust = json_result.illust
# print(">>> origin url: %s" % illust.image_urls['large'])

json_result = api.works(46363414)
print(json_result)
illust = json_result.response[0]
print( ">>> %s, origin url: %s" % (illust.caption, illust.image_urls['large']))

end_time = time.time()
print(end_time - start_time)