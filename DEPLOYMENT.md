# Deployment Guide

Since Vercel has a strict bundle size limit (250MB) that our map generation libraries exceed, we will use **Render** or **Railway**. Both offer free tiers or trial credits and support Docker natively.

## Option 1: Deploy to Render (Recommended for Free Tier)

1.  **Push your changes** to GitHub (I will do this for you).
2.  **Sign up/Log in** to [render.com](https://render.com/).
3.  Click **"New +"** -> **"Web Service"**.
4.  Select **"Build and deploy from a Git repository"** and click **Next**.
5.  Connect your GitHub account and select the **`maptoposter`** repository.
6.  Configure the service:
    *   **Name**: `maptoposter` (or simpler)
    *   **Region**: Closest to you (e.g., Singapore or Frankfurt).
    *   **Runtime**: **Docker** (This is important! Do not select Python).
    *   **Instance Type**: **Free**.
7.  Click **"Create Web Service"**.

Render will automatically build the Docker image and deploy it. It may take 5-10 minutes for the first build.

## Option 2: Deploy to Railway (Faster, Developer Friendly)

1.  **Sign up/Log in** to [railway.app](https://railway.app/).
2.  Click **"New Project"** -> **"Deploy from GitHub repo"**.
3.  Select the **`maptoposter`** repository.
4.  Railway will detect the `Dockerfile` and automatically build/deploy.

## Troubleshooting
-   **Build Failures**: Check the logs. If it complains about missing libraries for `osmnx` or `rtree`, the `Dockerfile` may need additional `apt-get install` packages, but the current one includes `libspatialindex-dev` which is the most common requirement.
-   **Memory Issues**: Generating very large maps (high distance) requires RAM. The free tiers have roughly 512MB RAM. If the app crashes during generation, try smaller distances (e.g., < 3000m).
