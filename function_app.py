from azure.functions import HttpResponse, HttpRequest, FunctionApp, AuthLevel
from core.handler import handle_fiis, handle_stocks

app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)


@app.route(route="fiis")
def get_fiis(req: HttpRequest) -> HttpResponse:
    result = handle_fiis(req.params.get("fiis"))
    return HttpResponse(result.body, mimetype=result.content_type, status_code=result.status_code)


@app.route(route="stocks")
def get_stocks(req: HttpRequest) -> HttpResponse:
    result = handle_stocks(req.params.get("stocks"))
    return HttpResponse(result.body, mimetype=result.content_type, status_code=result.status_code)
