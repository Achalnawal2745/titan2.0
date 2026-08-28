# Cron Job Patterns

## Common Schedules

**Every minute**: `* * * * *`  
**Every hour**: `0 * * * *`  
**Every day at midnight**: `0 0 * * *`  
**Every Monday at 9am**: `0 9 * * 1`  
**First day of month**: `0 0 1 * *`

## Best Practices

- Keep jobs idempotent (safe to run multiple times)
- Add logging and error handling
- Monitor job execution
- Use queues for heavy tasks
- Test thoroughly before production

## Use Cases

- Send daily email digests
- Clean up old data
- Generate reports
- Sync with external APIs
- Database maintenance
