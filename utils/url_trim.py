from urllib.parse import urlparse

def trim_tracking_params(url: str) -> str:

    tracking_params = {
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
        'pk_source', 'pk_medium', 'pk_campaign', 'pk_content',
        'fbclid', 'gclid', 'ga_source'
    }

    parsed_url = urlparse(url)

    if not parsed_url.query:
        return url

    query_string = parsed_url.query
    earliest_pos = len(query_string) + 1

    for param in tracking_params:
        pos = query_string.find(param + '=')
        if pos != -1 and pos < earliest_pos:
            earliest_pos = pos

    if earliest_pos > len(query_string):
        return url

    trimmed_query = query_string[:earliest_pos].rstrip('&')

    trimmed_url = (
            parsed_url.scheme + '://' +
            parsed_url.netloc +
            parsed_url.path +
            ('?' + trimmed_query if trimmed_query else '')
    )

    return trimmed_url
