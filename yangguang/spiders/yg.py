# -*- coding: utf-8 -*-
import scrapy
from yangguang.items import YangguangItem
import re


class YgSpider(scrapy.Spider):
    name = 'yg'
    allowed_domains = ['wz.sun07691.com']
    start_urls = ['http://wz.sun0769.com/index.php/question/report?page=']
    print("爬蟲開始...............")

    def parse(self, response):
        # 分組
        # tr_list = response.xpath("//div[@class='greyframe']/table[2]/tbody/tr/td/table/tbody/tr")
        tr_list = response.xpath("//div[@class='greyframe']/table[2]/tr/td/table/tr")
        print(len(tr_list))
        for tr in tr_list:
            item = YangguangItem()
            item["title"] = tr.xpath("./td[2]/a[@class='news14']/@title").extract_first()
            item["href"] = tr.xpath("./td[2]/a[@class='news14']/@href").extract_first()
            item["publish_date"] = tr.xpath("./td[last()]/text()").extract_first()

            yield scrapy.Request(
                item["href"],
                callback=self.parse_detail,
                meta={"item": item}  # 傳參數值(資料)到parse_detail
            )
        # 翻頁
        next_url = response.xpath("//a[text()='>']/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(
                next_url,
                callback=self.parse
            )

    def parse_detail(self, response):  # 處理詳情頁
        item = response.meta["item"]
        # 因為改版過,所以要判斷一下
        item["content"] = response.xpath("//div[@class='c1 text14_2']//text()").extract()
        item["content_img"] = response.xpath("//div[@class='c1 text14_2']//img/@src").extract()

        if item["content"] is None or len(item["content"]) == 0:
            # print("none")
            # print("title=", item["title"])
            # print("href=", item["href"])
            s = response.xpath("//div[@class='wzy1'][1]/table[2]//tr[1]/td[@class='txt16_3']//text()").extract()
            # s type是 list
            # 第一種方法格式化=====
            # t = "".join(s)
            # t = "".join(t.split())
            # item["content"] = t
            # 第二種方法格式化=========
            s = [re.sub(r"\xa0|\s", "", i) for i in s]
            t = [i for i in s if len(i) > 0]
            t = "".join(t)
            item["content"] = t
            # 第三種方法也可以在pipelines裡做格式化
            # print(t)
        else:
            print("yes")
            print(len(item["content"]))
            t = "".join(item["content"])
            t = "".join(t.split())
            item["content"] = t

        if item["content_img"] is None or len(item["content_img"]) == 0:
            item["content_img"] = response.xpath("//div[@class='wzy1'][1]/table[2]//tr[1]/td[@class='txt16_3']//img/@src").extract()
            item["content_img"] = ["http://wz.sun0769.com" + i for i in item["content_img"]]
        else:
            item["content_img"] = ["http://wz.sun0769.com" + i for i in item["content_img"]]
        # print(item)
        yield item
