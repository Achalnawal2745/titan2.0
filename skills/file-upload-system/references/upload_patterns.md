# File Upload Patterns

## Direct Upload
- Client → S3 directly (presigned URLs)
- Fastest, no server load
- Best for large files

## Server Upload
- Client → Server → S3
- More control, validation
- Good for small files

## Image Optimization
- Resize/compress before upload
- Generate thumbnails
- Convert formats (WebP)

## Security
- Validate file types
- Scan for malware
- Set size limits
- Use presigned URLs with expiration
