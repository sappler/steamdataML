import requests
import math
import pandas as pd
from selectolax.parser import HTMLParser


#a scraper to get a range of apps from the steam store, capturing price, year, reviews, vr support, tags
def main():
    tagfile = open("tags",'r')
    tagbase = eval(tagfile.read())
    tagfile.close()
    csv = open("db.csv",'a')
    csv.write('year,price,age_rating,tags,percent,total\n')
    for page in range(1,1420):
        src = gettext("https://store.steampowered.com/search/?sort_by=Reviews_DESC&ignore_preferences=1&page=" + str(page)) #displays every reviewed game on steam, 20 per page
        parsed = HTMLParser(src)
        div = parsed.css_first('[id=search_resultsRows]')
        for node in div.css('a'): #game per page
            att = node.attrs
            if "data-ds-bundleid" in att: #doesn't catch bundles
                continue
            try:
                href = att['href']
                if 'sub' in href:
                    continue
                print(att['href'])
                gametags = []
                i = 0
                temp = HTMLParser(gettext(att['href']))
                for tag in temp.css_first('.popular_tags').css('a.app_tag'): #tag per game
                    p = tag.text().strip().replace(' ','_')
                    if p in tagbase:
                        gametags.append(tagbase[p])
                        i+=1
                year = temp.css_first('.date').text().split(', ')[1]      # gets year of release
                #print(year)
                s = temp.css('.game_purchase_price') #gets price/ free status, assumes current price is original
                if s is None: #game is discounted
                    try:
                        price = str(
                            int(math.ceil(float(temp.css_first('.discount_original_price').text().strip().strip("$")))))
                    except:
                        #print('asd')
                        continue
                else: #game is normal price (could be free/demo)
                    for opt in s:
                        if 'Free' in opt.text():
                            price = '0'
                            break
                        elif 'Demo' in opt.text():
                            continue
                        price = str(int(math.ceil(float(opt.text().strip().strip("$")))))
                        break
                #print(price)
                try:
                    icon = temp.css_first('div.game_rating_icon')
                    grey = icon.css_first('img').attrs['src']
                    b = ('m.png' in grey)
                    if b:
                        agerating = '1'
                    else:
                        g = 1 / 0
                except:
                    agerating = '0'

                #print(agerating)
                reviewstr = temp.css('.nonresponsive_hidden.responsive_reviewdesc')[-1]
                spit = reviewstr.text().strip().split(' ')
                percent = spit[1].strip('%')
                total = spit[4].replace(',', '')
                #print(percent + ',' + total)
                gametags.sort()
                csv.write(year + ',' + price + ',' + agerating + ',' + str(gametags) + ',' + percent + ',' + total + '\n')
                temp.decompose()
            except:
                continue
    csv.close()
    return


def gettags(): #scrapes the 412 most popular tags from steam
    lsit = []
    dcit = {}
    parser = HTMLParser(gettext("https://store.steampowered.com/tag/browse/#global_492"))
    for tag in parser.css_first('div.tag_browse_tags').css('div.tag_browse_tag'):
        lsit.append(tag.text().strip().replace(' ','_'))
    lsit.sort()
    for i in range(0,len(lsit)):
        dcit[lsit[i]] = i
    objfile = open("tags",'w')
    objfile.write(str(dcit))
    objfile.close()


def gettext(url):
    with requests.Session() as session:
        content = session.get(url).text
    return content


if __name__ == '__main__':
    #gettags()
    main()
