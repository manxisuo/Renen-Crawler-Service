#coding:utf-8
import os, os.path
import time, urllib, getpass
from renren import RenRen
from thread_pool import Pool

# 登录
user = raw_input('输入邮箱:')
pw = getpass.getpass('输入密码:')
rr = RenRen()
uid = rr.login(user, pw)

time_s = time.time()

# 获取相册列表
albums = rr.get_albums()

# 计算照片总数
sum = 0
for album in albums:
    sum += album['photoCount']
print '照片总数:', sum

# 创建目录
if  not os.path.exists(uid):
    os.mkdir(uid)
for album in albums:
    album_dir = '%s/%s[%s]' % (uid, album['albumName'], album['photoCount'])
    if not os.path.exists(album_dir):
        os.mkdir(album_dir)

# 获取照片列表
def get_photo_list(album, out_q):
    photos = rr.get_photos(album['albumId'])
    for photo in photos:
        photo['album_info'] = album
        out_q.put(photo)

# 下载照片
def download_photo(photo):
    photoId = photo['photoId']
    album = photo['album_info']
    albumName = album['albumName']
    photoCount = album['photoCount']
    url = photo['url']
    photo_name = '%s/%s[%s]/%s.jpg' % (uid, albumName, photoCount, photoId)
    if not os.path.exists(photo_name):
        time_s = time.time()
        urllib.urlretrieve(url, photo_name)
        print '完成下载:', url
    else:
        print '照片已存在:', photo_name
        pass

pool_1 = Pool(albums)
out_q = pool_1.sumbit_task_with_out_queue(get_photo_list, 20)

pool_2 = Pool(out_q)
pool_2.submit_task(download_photo, 50)

pool_1.join()
pool_2.join()

print '总耗时:%s秒' % (time.time() - time_s)
