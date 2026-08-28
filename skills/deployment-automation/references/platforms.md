# Deployment Platforms Reference

## Supported Platforms

### 1. Vercel
**Best For**: Next.js, React, static sites  
**Pricing**: Free tier available  
**CLI**: `npm install -g vercel`  
**Deploy**: `vercel --prod`

**Features**:
- Automatic HTTPS
- Global CDN
- Preview deployments
- Environment variables
- Custom domains

**Configuration**: `vercel.json`

---

### 2. Railway
**Best For**: Full-stack apps, databases, backend services  
**Pricing**: $5/month minimum  
**CLI**: `npm install -g @railway/cli`  
**Deploy**: `railway up`

**Features**:
- PostgreSQL, MySQL, Redis included
- Environment variables
- Automatic deployments
- Custom domains
- Logs and metrics

**Configuration**: `railway.toml` or `railway.json`

---

### 3. Netlify
**Best For**: Static sites, JAMstack  
**Pricing**: Free tier available  
**CLI**: `npm install -g netlify-cli`  
**Deploy**: `netlify deploy --prod`

**Features**:
- Continuous deployment
- Forms handling
- Serverless functions
- Split testing
- Custom domains

**Configuration**: `netlify.toml`

---

### 4. Heroku
**Best For**: Traditional web apps, APIs  
**Pricing**: $7/month per dyno  
**CLI**: `curl https://cli-assets.heroku.com/install.sh | sh`  
**Deploy**: `git push heroku main`

**Features**:
- Add-ons marketplace
- Postgres included
- Logs
- Scaling
- Custom domains

**Configuration**: `Procfile`

---

## Platform Selection Guide

### Choose Vercel If:
- Using Next.js or React
- Need fast global CDN
- Want preview deployments
- Deploying frontend only

### Choose Railway If:
- Need database included
- Building full-stack app
- Want simple pricing
- Need backend services

### Choose Netlify If:
- Building static site
- Using JAMstack
- Need forms handling
- Want serverless functions

### Choose Heroku If:
- Using traditional frameworks (Rails, Django, etc.)
- Need extensive add-ons
- Want mature ecosystem
- Familiar with Heroku workflow

---

## Environment Variables

### Vercel
```bash
vercel env add VARIABLE_NAME
vercel env pull
```

### Railway
```bash
railway variables set VARIABLE_NAME=value
railway variables
```

### Netlify
```bash
netlify env:set VARIABLE_NAME value
netlify env:list
```

### Heroku
```bash
heroku config:set VARIABLE_NAME=value
heroku config
```

---

## Custom Domains

### Vercel
```bash
vercel domains add example.com
vercel domains ls
```

### Railway
- Add domain in Railway dashboard
- Configure DNS records

### Netlify
```bash
netlify domains:add example.com
netlify domains:list
```

### Heroku
```bash
heroku domains:add example.com
heroku domains
```

---

## Rollback

### Vercel
```bash
vercel rollback
```

### Railway
- Rollback in Railway dashboard
- Or redeploy previous commit

### Netlify
```bash
netlify rollback
```

### Heroku
```bash
heroku rollback
```

---

## Logs

### Vercel
```bash
vercel logs
```

### Railway
```bash
railway logs
```

### Netlify
```bash
netlify logs
```

### Heroku
```bash
heroku logs --tail
```

---

## Best Practices

1. **Use Environment Variables** - Never commit secrets
2. **Test Locally First** - Use preview/staging deployments
3. **Monitor Deployments** - Check logs after deploy
4. **Set Up Alerts** - Get notified of failures
5. **Document Process** - Keep deployment notes
6. **Automate CI/CD** - Use GitHub Actions
7. **Version Control** - Tag releases
8. **Health Checks** - Implement /health endpoint
9. **Graceful Shutdown** - Handle SIGTERM
10. **Database Migrations** - Run before deployment

---

## Troubleshooting

### Build Fails
- Check build logs
- Verify dependencies
- Test build locally
- Check Node version

### Deploy Succeeds But Site Broken
- Check runtime logs
- Verify environment variables
- Test API endpoints
- Check database connection

### Slow Performance
- Enable CDN
- Optimize images
- Use caching
- Check database queries

### Environment Variables Missing
- Verify variables set
- Check variable names
- Restart deployment
- Check scoping (preview vs production)

---

## Migration Guide

### From Heroku to Railway
1. Export Heroku config: `heroku config -s > .env`
2. Import to Railway: `railway variables set $(cat .env)`
3. Update database connection string
4. Deploy: `railway up`

### From Netlify to Vercel
1. Export Netlify config
2. Create `vercel.json`
3. Set environment variables
4. Deploy: `vercel --prod`

### From Vercel to Railway
1. Export environment variables
2. Create `railway.toml`
3. Set up database if needed
4. Deploy: `railway up`

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | Best Value |
|----------|-----------|-----------|------------|
| Vercel | 100GB bandwidth | $20/mo | Frontend |
| Railway | $5 credit | $5/mo minimum | Full-stack |
| Netlify | 100GB bandwidth | $19/mo | Static |
| Heroku | No free tier | $7/dyno | Traditional |

---

## Recommended Stack

**Frontend Only**: Vercel  
**Full-Stack**: Railway  
**Static Site**: Netlify  
**Microservices**: Railway or Heroku  
**Enterprise**: Heroku or custom

---

## Quick Reference

```bash
# Vercel
vercel --prod                    # Deploy to production
vercel --preview                 # Deploy preview
vercel env pull                  # Pull environment variables

# Railway
railway up                       # Deploy
railway logs                     # View logs
railway variables                # List variables

# Netlify
netlify deploy --prod            # Deploy to production
netlify deploy                   # Deploy preview
netlify env:list                 # List variables

# Heroku
git push heroku main             # Deploy
heroku logs --tail               # View logs
heroku config                    # List variables
```
