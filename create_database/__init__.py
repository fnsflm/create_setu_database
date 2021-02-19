import os
import json

class Pixiv:
    def __init__(self,user,passwd):
        self.user = user
        self.passwd = passwd

class Configs:

    def __init__(self):
        f = open("config.json")
        js = json.load(f)
        self.saucenao_key = js['saucenao_key']
        self.dowlaod_origin = js['dowlaod_origin']
        self.move = js['move']
        js_pix = js['pixiv']
        self.pixiv = Pixiv(js_pix['user'],js_pix['passwd'])
        f.close()

    @classmethod
    def before_get_config(self):
        if not os.path.exists("config.json"):
            f = open("config.json", 'w')
            f.write("""{
    \"saucenao_key\": \"must set it !\",
    \"dowlaod_origin\": true,
    \"move\": 0
}\n""")
            f.close()

Configs.before_get_config()
configs = Configs()
