import requests
import cbor

from utils.response import Response

def download(url, config, logger=None):
    host, port = config.cache_server
    try:
        resp = requests.get(
            f"http://{host}:{port}/",
            params=[("q", f"{url}"), ("u", f"{config.user_agent}")], timeout=10)
    except requests.exceptions.Timeout:
        return Response({
            "error": f"Timeout Error with url {url}.",
	        "status": 404,
            "url": url})
    if resp:
        return Response(cbor.loads(resp.content))
    logger.error(f"Spacetime Response error {resp} with url {url}.")
    return Response({
        "error": f"Spacetime Response error {resp} with url {url}.",
        "status": resp.status_code,
        "url": url})
