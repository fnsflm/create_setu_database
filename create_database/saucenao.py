# This script requires Python 3+, Requests, and Pillow, a modern fork of PIL, the Python Imaging Library: 'easy_install Pillow' and 'easy_install requests'

from create_database import configs
from main import org_path
import sys
import os
import io
import requests
from PIL import Image
import json
import codecs
import re
import time
from collections import OrderedDict
import shutil

api_key = configs.saucenao_key
minsim = '80!'  # forcing minsim to 80 is generally safe for complex images, but may miss some edge cases. If images being checked are primarily low detail, such as simple sketches on white paper, increase this to cut down on false positives.

sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
thumbSize = (250, 250)


# encoded print - handle random crap
def printe(line):
    print(str(line).encode(sys.getdefaultencoding(), 'replace'))  # ignore or replace


pth = org_path
if len(sys.argv) > 1:
    pth = sys.argv[1]
for root, _, files in os.walk(pth, topdown=False):
    for f in files:
        fname = os.path.join(root, f)
        for ext in extensions:
            if fname.lower().endswith(ext):
                print(fname)
                image = Image.open(fname)
                image = image.convert('RGB')
                image.thumbnail(thumbSize, resample=Image.ANTIALIAS)
                imageData = io.BytesIO()
                image.save(imageData, format='PNG')

                url = 'http://saucenao.com/search.php?output_type=2&numres=1' \
                      '&minsim=' + minsim + '&api_key=' + api_key
                files = {'file': ("image.png", imageData.getvalue())}
                imageData.close()

                processResults = True
                while True:
                    r = requests.post(url, files=files)
                    if r.status_code != 200:
                        if r.status_code == 403:
                            print('Incorrect or Invalid API Key! Please Edit Script to Configure...')
                            sys.exit(1)
                        else:
                            # generally non 200 statuses are due to either overloaded servers or the user is out of searches
                            print("status code: " + str(r.status_code))
                            time.sleep(10)
                    else:
                        results = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(r.text)
                        if int(results['header']['user_id']) > 0:
                            # api responded
                            print(
                                'Remaining Searches 30s|24h: ' + str(results['header']['short_remaining']) + '|' + str(
                                    results['header']['long_remaining']))
                            if int(results['header']['status']) == 0:
                                # search succeeded for all indexes, results usable
                                break
                            else:
                                if int(results['header']['status']) > 0:
                                    # One or more indexes are having an issue.
                                    # This search is considered partially successful, even if all indexes failed, so is still counted against your limit.
                                    # The error may be transient, but because we don't want to waste searches, allow time for recovery.
                                    print('API Error. Retrying in 600 seconds...')
                                    time.sleep(600)
                                else:
                                    # Problem with search as submitted, bad image, or impossible request.
                                    # Issue is unclear, so don't flood requests.
                                    print('Bad image or other request error. Skipping in 10 seconds...')
                                    processResults = False
                                    time.sleep(10)
                                    break
                        else:
                            # General issue, api did not respond. Normal site took over for this error state.
                            # Issue is unclear, so don't flood requests.
                            print('Bad image, or API failure. Skipping in 10 seconds...')
                            processResults = False
                            time.sleep(10)
                            break

                if processResults:

                    if int(results['header']['results_returned']) > 0:
                        # one or more results were returned
                        if float(results['results'][0]['header']['similarity']) > float(
                                results['header']['minimum_similarity']):
                            print('hit! ' + str(results['results'][0]['header']['similarity']))

                            # get vars to use
                            service_name = ''
                            illust_id = 0
                            member_id = -1
                            index_id = results['results'][0]['header']['index_id']
                            page_string = ''
                            page_match = re.search('(_p[\d]+)\.', results['results'][0]['header']['thumbnail'])
                            urls = results['results'][0]['data']['ext_urls']
                            if page_match:
                                page_string = page_match.group(1)

                            if index_id == 5 or index_id == 6:
                                # 5->pixiv 6->pixiv historical
                                service_name = 'pixiv'
                                member_id = results['results'][0]['data']['member_id']
                                illust_id = results['results'][0]['data']['pixiv_id']
                                if configs.move == 1:
                                    shutil.copy(fname, "result/pixiv/")
                                if configs.move == 2:
                                    shutil.move(fname, "result/pixiv/")
                                with open("result/pixiv/pic_list.tsv", 'a+') as srch_res:
                                    srch_res.write("%s\t%s\n" % (fname, urls))
                                    srch_res.close()
                            else:
                                if configs.move == 1:
                                    shutil.copy(fname, "result/other/")
                                if configs.move == 2:
                                    shutil.move(fname, "result/other/")
                                with open("result/other/pic_list.tsv", 'a+') as srch_res:
                                    srch_res.write("%s\t%s\n" % (fname, urls))
                                    srch_res.close()
                                print('not pixiv')

                            print('urls', urls)
                            print('uid', member_id)
                            print('pid', illust_id)

                        else:
                            print('miss... ' + str(results['results'][0]['header']['similarity']))

                    else:
                        if configs.move == 1:
                            shutil.copy(fname, "result/unknow/")
                        if configs.move == 2:
                            shutil.move(fname, "result/unknow/")
                        with open("result/unknow/pic_list.tsv", 'a+') as srch_res:
                            srch_res.write("%s\n" % fname)
                            srch_res.close()
                        print('no results... ;_;')

                    if int(results['header']['long_remaining']) < 1:  # could potentially be negative
                        print('Out of searches for today. Sleeping for 6 hours...')
                        time.sleep(6 * 60 * 60)
                    if int(results['header']['short_remaining']) < 1:
                        print('Out of searches for this 30 second period. Sleeping for 25 seconds...')
                        time.sleep(25)

print('All Done!')
