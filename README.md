# StockMarketScrapyAzFunc

Multi-cloud serverless application (Azure Functions & AWS Lambda) that scrapes financial data from the Brazilian stock market using [Scrapy](https://scrapy.org/). Exposes HTTP endpoints to fetch real-time information about **FIIs** (Fundos de Investimento Imobiliário) and **Stocks**.

## Data Sources

| Endpoint | Source | Data |
|----------|--------|------|
| `/api/fiis` | [fundsexplorer.com.br](https://www.fundsexplorer.com.br) | Price, status, DY, P/VP, net worth, last dividend, rend distribution, management reports |
| `/api/stocks` | [investidor10.com.br](https://investidor10.com.br) | Price, P/L, P/VP, DY, ROE, CAGR, debt/EBITDA, dividend history, sector, management reports |

## Project Structure

```
├── core/handler.py          # Platform-agnostic business logic
├── function_app.py          # Azure Functions entry point (HTTP routes)
├── lambda_handler.py        # AWS Lambda entry point
├── envs.py                  # Environment configuration
├── scrapy.cfg               # Scrapy project config
├── requirements.txt         # Python dependencies
├── template.yaml            # AWS SAM deployment template
├── host.json                # Azure Functions host config
├── local.settings.json      # Local dev settings
└── FIIsScraping/
    ├── items.py             # Scrapy Item definitions (data models)
    ├── pipelines.py         # Data cleaning & transformation
    ├── run_spiders.py       # Spider runner (multiprocessing wrapper)
    ├── settings.py          # Scrapy settings
    ├── middlewares.py        # Spider & downloader middlewares
    └── spiders/
        ├── fiis_scraper.py  # FII spider
        └── stock_scraper.py # Stock spider
```

## Tech Stack

- **Runtime**: Azure Functions v2 / AWS Lambda (Python 3.12)
- **Scraping**: Scrapy 2.11 + Twisted
- **Anti-detection**: scrapy-fake-useragent

## Prerequisites

- Python 3.9+
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)

## Setup

```bash
# Create and activate virtual environment
python -m venv venvs
source venvs/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run locally

```bash
func host start
```

### API Endpoints

**GET /api/fiis** — Scrape FII data

```bash
# Single FII
curl "http://localhost:7071/api/fiis?fiis=XPML11"

# Multiple FIIs (comma-separated)
curl "http://localhost:7071/api/fiis?fiis=XPML11,MXRF11"
```

**GET /api/stocks** — Scrape stock data

```bash
# Single stock
curl "http://localhost:7071/api/stocks?stocks=ITSA3"

# Multiple stocks (comma-separated)
curl "http://localhost:7071/api/stocks?stocks=ITSA3,PETR4"
```

### Example Response (FII)

```json
[
  {
    "url": "https://www.fundsexplorer.com.br/funds/xpml11",
    "fii_type": "Tijolo: Shoppings",
    "name": "XP Malls",
    "code": "XPML11",
    "status": "0,06%",
    "current_price": "R$ 106,29",
    "average_daily": "R$ 11,8 M",
    "last_dividend": "R$ 0,92",
    "dividend_yield": "10,42%",
    "net_worth": "R$ 6,7B",
    "p_vp": "0,90",
    "last_dividend_yield": "0,89%",
    "rend_distribution": {
      "dividend": "R$ 0,92",
      "future_pay_day": "25/04/2025",
      "income_percentage": "0,89%",
      "data_com": "16/04/2025"
    },
    "reports_link": "https://www.fundamentus.com.br/fii_relatorios.php?papel=XPML11",
    "last_management_report": {
      "link": "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=897324&cvm=true",
      "date": "08/05/2025"
    }
  }
]
```

## Deployment

### Azure Functions

```bash
func azure functionapp publish <function_app_name> --build remote --publish-local-settings
```

### AWS Lambda

Deploy using AWS SAM:

```bash
sam build
sam deploy --guided
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RUN_ENV` | Set to `azure` or `aws` to write data files to `/tmp/` | `""` (writes to project root) |
