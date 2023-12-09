# Florida Compensation Scraper

This Scrapy project is designed to scrape Florida compensation claims data from [www.jcc.state.fl.us](https://www.jcc.state.fl.us/JCC/searchJCC/searchDisplay.asp).

## Requirements

- Scrapy==2.11.0
- Selenium==4.15.2

## Installation

1. Clone the repository:

    ```bash
    git clone git@github.com:EhsanSafir/Florida-Compensation-Scraper.git
    cd <repository-directory>
    ```

2. Install dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

## How to Run

To run the scraper, use the following command:

```bash
scrapy crawl spider -a start_page=<start_page_number> -a end_page=<end_page_number>
```
