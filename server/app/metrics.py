from prometheus_client import Counter, Histogram

req_counter = Counter("api_requests_total", "Requests", ["path", "method", "status"])
latency_hist = Histogram("api_latency_seconds", "Latency", ["path", "method"])
