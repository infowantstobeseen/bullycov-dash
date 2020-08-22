# MSState COVID Dashboard

This is a simple dashboard for the [Mississippi State University COVID-19 Campus Testing site](https://www.msstate.edu/covid19/campus-testing "Latest COVID-19 Campus Testing") that describes the last week's data since the beginning of the Fall 2020 semester. Its embedded on my blog (though can be embedded freely) and uses [my simple scraper](https://github.com/infowantstobeseen/bullycov-scrape "MSState COVID Scraper").

## Usage

Run the Python3 script; it will read from the [scraped data](https://github.com/infowantstobeseen/bullycov-scrape/blob/main/bullycov.json "MSState COVID Scraper data") and generate the HTML fragment `bullycov-dash.html` for embedding via an iframe. 
