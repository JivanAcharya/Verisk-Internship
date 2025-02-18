import scrapy

class UniSpider(scrapy.Spider):
    name = "uni"
    start_urls=['https://www.topuniversities.com/where-to-study/north-america/united-states/ranked-top-100-us-universities']

    def parse(self, response):
        for uni in response.css('div.ranking-data-row_US-100-2025.ranking-data-row'):
            try:
                yield {
                    'rank':uni.css('div.col-sm-12.col-md-2.rank::text').get(),
                    'name':uni.css('a::text').get(),
                    'location':uni.css('div.col-sm-12.col-md-2.d-none.d-sm-block.location::text').get(),
                    'more_info':uni.css('a').attrib['href'],
                }
            except:
                pass

        next_page = response.css('a.page-link.next').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback = self.parse)