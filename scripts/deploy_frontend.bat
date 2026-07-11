@echo off
cd /d C:\Users\forrydev\Desktop\SpyFy
vercel --prod --yes -e NEXT_PUBLIC_API_URL=https://spyfy-api.onrender.com >> C:\Users\forrydev\Desktop\SpyFy\vercel_deploy.out 2>&1
