# -*- coding: utf-8 -*-
import os


def rmQ(fname):
    return fname.split("?")[0]  # 保存するファイル名から「？」以下を削除


def getImgURL(src, url):
    if "http" not in src:
        return url + src  # 他ページからのリンクに対応
    else:
        return src


def mkdir(dirName):
    try:
        os.mkdir(dirName)  # ディレクトリ作成
    except Exception as e:
        print e


# pass # if dirName already exist

def DLImages(AllImages, url, dirName):
    import urllib

    successNum = 0
    for img in AllImages:
        src = img.get("src")  # imgタグのsrcを取得
        imgURL = getImgURL(src, url)
        fname = src.split("/")[-1]

        if "?" in fname:
            fname = rmQ(fname)
        try:
            if fname in os.listdir(dirName):
                fname = fname + str(successNum)
            urllib.urlretrieve(imgURL, dirName + "/" + fname)  # 作成したディレクトリに保存
            print "[ Success ] " + imgURL
            successNum += 1
        except Exception as e:
            print e
            print "[ Failed ] " + imgURL

    return successNum  # ダウンロード成功の数を返す


def main(url="http://www.nikkei.com/", dirName="./DLImages"):
    from bs4 import BeautifulSoup
    import urllib2

    mkdir(dirName)
    response = urllib2.urlopen(url)  # ページオープン
    html = response.read()  # html取得
    soup = BeautifulSoup(html)
    AllImages = soup.find_all("img")  # 全imgタグを取得
    imgNum = len(AllImages)
    successNum = DLImages(AllImages, url, dirName)

    print successNum, "images could be downloaded (in", imgNum, "images)."


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])