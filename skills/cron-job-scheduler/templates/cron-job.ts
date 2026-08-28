// Cron Job Template
import { scheduleJob } from '@/lib/cron';

// Daily at midnight
scheduleJob('0 0 * * *', async () => {
  console.log('Running daily job...');
  // Your task here
});

// Every hour
scheduleJob('0 * * * *', async () => {
  console.log('Running hourly job...');
});

// Every Monday at 9am
scheduleJob('0 9 * * 1', async () => {
  console.log('Running weekly job...');
});
