import logging
import scrapy
from scrapy import Selector
from ..items import CaseItem
from ..utils import to_snake_case
from ..selinum_utils import start_selenium_to_create_session


class ResultSpider(scrapy.Spider):
    pagination_url_template = "https://www.jcc.state.fl.us/JCC/searchJCC/searchDisplay.asp?pc=%s"
    name = "spider"
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'LOG_LEVEL': logging.ERROR
    }

    def start_requests(self):
        # Create a CookieJar to manage cookies
        self._cookie = start_selenium_to_create_session()
        self.start_page = int(getattr(self, 'start_page', 1))
        self.end_page = int(getattr(self, 'end_page', 50))
        url = self.pagination_url_template % self.start_page
        yield scrapy.Request(url=url, callback=self.parse, cookies=self._cookie)

    def parse(self, response):
        # pagination info
        pagination_raw_data = response.css('.grid_3 h5::text').get()
        current_page, total_page = pagination_raw_data.split(':')[-1].split('of')
        current_page = int(current_page)
        total_page = int(total_page)
        has_next_page = current_page <= total_page
        must_finish_scrapping = current_page == self.end_page
        next_page_url = self.pagination_url_template % (current_page + 1)
        print(
            f'[x] Result Page {current_page}/{self.end_page} started | hase next page : {has_next_page} | must_finish_scrapping : {must_finish_scrapping} ')
        # parse the result page items
        raw_items: [Selector] = response.css('#main .alignleft p')
        for index, raw_item in enumerate(raw_items, 1):
            parsed_item_url = "https://www.jcc.state.fl.us" + raw_item.css('a::attr(href)').get()

            yield scrapy.Request(url=parsed_item_url, callback=self._specific_case_parser)
        if (not must_finish_scrapping) and has_next_page:
            yield scrapy.Request(url=next_page_url, callback=self.parse)

    def _specific_case_parser(self, response):
        # parse the result page items

        is_applicable_case, docket_data = self._docket_tab_parser(response)
        print("[x] Docket Tab extracted")
        if is_applicable_case:
            summery_data = self._case_summery_parser(response)
            print("[x] Case Summery Info Extracted")
            schedule = self.schedule_tab_parser(response)
            print("[x] Case schedule Info Extracted")
            pfbs = self.pfbs_tab_parser(response)
            print("[x] Case pfbs Info Extracted")
            data_item = {
                **summery_data,
                'docket_data': docket_data,
                'schedule': schedule,
                'pfbs': pfbs
            }
            item = CaseItem(**data_item)
            print("[x] Case pfbs Info Extracted")
            yield item

    def _case_summery_parser(self, response):
        case_number = response.css('h1 > .no-break::text').get().strip()
        case_name = ' '.join(response.css('#CaseStyle div[align="center"]::text').getall())
        all_keys = response.css('#CaseStyle .grid_2::text').getall()
        # normalize the keys
        all_keys = list(map(lambda x: x.rstrip(':'), all_keys))
        # all values
        all_values = response.css('#CaseStyle .grid_6.nomargin::text').getall()
        # combine key and values together using zip
        summery_data = {
            "case_number": case_number,
            "case_name": case_name
        }
        for key, value in zip(all_keys, all_values):
            clean_key = to_snake_case(key)
            summery_data[clean_key] = value
        return summery_data

    def _docket_tab_parser(self, response):
        is_applicable_case = False
        raw_rows = response.css('#docket table tr:not(:first-child)')
        tables_row = []
        for row in raw_rows:
            pdf_link = row.css('td:nth-child(1) a::attr(href)').get()
            pdf_link = f'https://www.jcc.state.fl.us/{pdf_link}'
            date = row.css('td:nth-child(2)::text').get()
            proceedings = row.css('td:nth-child(3)::text').get().strip()
            if proceedings in ['Settlement Order- Represented', 'Settlement Order- Pro Se']:
                is_applicable_case = True
            tables_row.append({'PDF': pdf_link, 'Date': date, 'proceedings': proceedings})
        return is_applicable_case, tables_row

    def schedule_tab_parser(self, response):
        raw_rows = response.css('#schedule table tr:not(:first-child)  ')
        table_rows = []
        for row in raw_rows:
            is_not_empty = len(row.css('td[colspan="5"]')) == 0
            if is_not_empty:
                hearing_type = row.css('td:nth-child(1)::text').get()
                event_date = row.css('td:nth-child(2)::text').get()
                start_time = row.css('td:nth-child(3)::text').get()
                current_status = row.css('td:nth-child(4)::text').get()
                with_whom = row.css('td:nth-child(5)::text').get()
                table_rows.append({'hearing type': hearing_type, 'event_date': event_date, "start_time": start_time,
                                   "current_status": current_status, "with_whom": with_whom})
        return table_rows

    def pfbs_tab_parser(self, response):
        # Select the table rows containing petitions
        petition_rows = response.css('#Petitions > tr:not(:first-child)')
        petitions_data = []
        for row in petition_rows:
            date_filed = row.css('td:nth-child(1)::text').get()
            petition_link = row.css('td:nth-child(2) a::attr(href)').get()
            petition_text = row.css('td:nth-child(2) a::text').get().strip()

            # Extract issues data if present
            issues_data = self.extract_issues_data(row)
            petition_entry = {
                'Date Filed': date_filed,
                'Petition Link': petition_link,
                'Petition Text': petition_text,
                'Issues': issues_data,
            }
            petitions_data.append(petition_entry)
        return petitions_data

    def extract_issues_data(self, row):
        # Select the issues table rows
        issues_rows = row.css('td:nth-child(2) #PetIssues  tr:not(:first-child)')
        issues_data = []
        for issues_row in issues_rows:
            issue_description = issues_row.css('td:nth-child(1)::text').get()
            status = issues_row.css('td:nth-child(2)::text').get()
            begin_date = issues_row.css('td:nth-child(3)::text').get()
            end_date = issues_row.css('td:nth-child(4)::text').get()
            issue_entry = {
                'Issue Description': issue_description,
                'Status': status,
                'Begin Date': begin_date,
                'End Date': end_date,
            }
            issues_data.append(issue_entry)
        return issues_data
