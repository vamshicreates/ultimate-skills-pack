# Draft schema

Save the final content in this JSON shape before validation or publishing:

```json
{
  "source_url": "https://example.com/article",
  "format": "single",
  "language": "English",
  "posts": [
    "The complete news post, including the article URL when appropriate."
  ],
  "cta_reply": "Download the UTV Hott News app:\nAndroid: https://play.google.com/store/apps/details?id=com.mroads.reporterapp\niPhone: https://apps.apple.com/us/app/its-utv-hott-news-telugu/id6755475182"
}
```

Allowed `format` values are `single` and `thread`. A single draft has exactly one item in `posts`; a thread has two or more items in publishing order.

Run the validator from the skill directory:

```text
python3 scripts/validate_posts.py /path/to/draft.json
```

Use `py -3` on Windows. Delete temporary drafts after publishing when they are no longer needed.
