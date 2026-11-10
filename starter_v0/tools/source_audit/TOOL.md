---
name: source_audit
track: core
kind: local_formatter
requires_env: []
inputs: [items]
outputs: [item_count, unique_url_count, duplicate_urls, source_counts]
side_effect: false
---
# source_audit

Checks already-collected research items for repeated URLs and counts items per source. Use it after collecting results when you need to spot duplicated links or understand source coverage. Do not use it to search for sources, assess credibility, or verify factual claims; it makes no network requests.
