#coding:utf-8
import json, re
import requests, demjson

LOGIN_PAGE = "http://www.renren.com/PLogin.do"
ALBUMS_PAGE = "http://photo.renren.com/photo/{uid}/albumlist/v7?showAll=1"
PHOTOS_PAGE = "http://photo.renren.com/photo/{uid}/album-{aid}/bypage/ajax/v7?page={page}&pageSize={size}"
PHOTOS_PAGE_MAX_SIZE = 100

RE_USER = re.compile(r"nx\.user\s*=\s*({.*?})", re.M | re.S)
RE_ALBUMS = re.compile(r"^'albumList':\s*(.+),$", re.M)

class RenRen():
    def __init__(self):
        self.session = requests.Session()
        self.uid = None
        self.user_info = {} #id, ruid, tinyPic, name, requestToken, _rtk

    # 登录
    def login(self, user, password):
        r = self.session.post(LOGIN_PAGE, params = {"email": user, "password": password})
        self.uid = r.url.split('/')[-1]
        match = RE_USER.search(r.text)
        if match:
            text = match.group(1)
            self.user_info = demjson.decode(text)
        return self.uid
        
    # 获取相册列表
    def get_albums(self, uid = None):
        '''
        'albumId', 'albumName', 'cover', 'ownerId', 'photoCount, 'sourceControl', 'type'
        '''        
        if uid is None:
            uid = self.uid
        r = self.session.get(ALBUMS_PAGE.format(uid = uid))
        match = RE_ALBUMS.search(r.text)
        if match:
            albums = json.loads(match.group(1))
            return albums
        return None

    # 获取照片列表
    def get_photos(self, albumId, uid = None):
        '''
        'photoId', 'albumId', 'width', 'height', 'isLike',
        'ownerId', 'position', 'positionSaved', 'url', 'photoAtExt'
        '''
        if uid is None:
            uid = self.uid
        photos = []
        page = 1
        while True:
            url = PHOTOS_PAGE.format(uid = uid, aid = albumId, page = page, size = PHOTOS_PAGE_MAX_SIZE)
            resp = self.session.get(url)
            if resp.status_code is 200:
                photoList = resp.json()['photoList']
                photos.extend(photoList) 
                if len(photoList) < PHOTOS_PAGE_MAX_SIZE:
                    break
            page += 1
        return photos
