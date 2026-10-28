# REST API Reference

Use these endpoints if MCP is not available.

## Base URL
```
https://app.thumbcraft.io/api/v1
```

## Authentication
All requests require:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Generate Thumbnail
```http
POST /thumbnails
Content-Type: application/json

{
  "prompt": "A surprised man looking at camera...",
  "styleId": "style_xxx",
  "brandId": "brand_xxx",
  "faceIds": ["face_xxx"],
  "aspectRatio": "16:9"
}
```

**Response:**
```json
{
  "success": true,
  "thumbnail": {
    "id": "thumb_xxx",
    "pngUrl": "https://...",
    "webpUrl": "https://..."
  }
}
```

### Analyze Video
```http
POST /videos/analyze
Content-Type: application/json

{
  "youtubeUrl": "https://youtube.com/watch?v=..."
}
```

**Response:**
```json
{
  "success": true,
  "videoTitle": "Original Video Title",
  "videoSummary": "Brief summary...",
  "thumbnailConcepts": [
    {
      "id": "concept_1",
      "title": "Concept Name",
      "description": "Why this works",
      "prompt": "Ready-to-use prompt...",
      "emotionalHook": "The psychology behind it"
    }
  ]
}
```

### List Styles
```http
GET /styles
```

### List Faces
```http
GET /faces?activeOnly=true
```

### List Brands
```http
GET /brands
```

### Generate SEO Titles
```http
POST /seo/titles
Content-Type: application/json

{
  "youtubeUrl": "https://youtube.com/watch?v=..."
}
```

### Generate SEO Description
```http
POST /seo/description
Content-Type: application/json

{
  "youtubeUrl": "https://youtube.com/watch?v=..."
}
```

### Get Credits
```http
GET /credits
```

**Response:**
```json
{
  "tier": "creator",
  "credits": {
    "total": 150,
    "purchased": 50,
    "subscription": 100
  },
  "canGenerate": true
}
```

## Rate Limits

| Tier | Requests/Minute |
|------|-----------------|
| Free | 20 |
| Starter | 60 |
| Creator | 120 |
| Agency | 300 |

Rate limit headers in responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## Error Responses

```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request / Invalid parameters |
| 401 | Missing or invalid API key |
| 402 | Insufficient credits |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Server error |
