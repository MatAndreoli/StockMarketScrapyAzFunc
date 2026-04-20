from core.handler import handle_fiis, handle_stocks


def lambda_handler(event, context):
    path = event.get("rawPath", "") or event.get("path", "")
    params = event.get("queryStringParameters") or {}

    if path.endswith("/fiis"):
        result = handle_fiis(params.get("fiis"))
    elif path.endswith("/stocks"):
        result = handle_stocks(params.get("stocks"))
    else:
        return {"statusCode": 404, "body": "Not found"}

    return {
        "statusCode": result.status_code,
        "headers": {"Content-Type": result.content_type},
        "body": result.body,
    }
