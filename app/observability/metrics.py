from prometheus_client import Counter, Gauge, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

events_provider_requests_total = Counter(
    "events_provider_requests_total",
    "Total number of HTTP requests made to the external events provider API",
    ["endpoint", "status"],
)

events_provider_request_duration_seconds = Histogram(
    "events_provider_request_duration_seconds",
    "Duration of HTTP requests to the external events provider API in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

tickets_created_total = Counter(
    "tickets_created_total", "Total number of tickets successfully created"
)

tickets_cancelled_total = Counter(
    "tickets_cancelled_total", "Total number of tickets successfully cancelled"
)

events_total = Gauge("events_total", "Current number of events stored in the database")

cache_hits_total = Counter("cache_hits_total", "Total number of cache hits")

cache_misses_total = Counter("cache_misses_total", "Total number of cache misses")
