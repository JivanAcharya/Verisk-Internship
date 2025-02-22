import scrapy

#for qsrankings website
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


# from shangai rankings getting the urls of the universities
# Gets onlyfrom the give or shown page, cant do multiple pages
class InstitutionSpider(scrapy.Spider):
    name = 'institution_spider'
    start_urls = ['https://www.shanghairanking.com/rankings/arwu/2024']  # Start URL

    def parse(self, response):
        # Extract all institution URLs from the table
        table = response.css("table.rk-table")
        link_container =table.css("div.link-container")
        institution_links = link_container.css("a::attr(href)").getall()

        institution_links = ["https://www.shanghairanking.com" + link for link in institution_links]

        # Loop through each institution link
        for link in institution_links:
            # Follow the link to the institution's page
            yield response.follow(link, self.parse_institution)

    def parse_institution(self, response):
        # Extract the contact-item a tag href
        contact_link = response.css("div.contact-item a::attr(href)").get()

        if contact_link:
            yield {
                'institution': response.url,
                'contact_url': contact_link
            }


