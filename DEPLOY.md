# 📤 Publishing to GitHub

## Preparation

1. **Check files:**
   - ✅ README.md — filled
   - ✅ LICENSE — added
   - ✅ .gitignore — configured
   - ✅ .env — must NOT be in repository!

2. **Clean cache:**
   ```bash
   # Remove __pycache__
   for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"
   
   # Remove test files
   del test_*.py
   ```

## Create Repository

1. Go to https://github.com/new
2. Enter name: `yandex-podcast-downloader-vkbot`
3. Choose **Private** or **Public**
4. Click **Create repository**

## Publish

### If Git is not installed:

1. Download Git: https://git-scm.com/download/win
2. Open terminal in project folder:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: VK bot for Yandex Music podcasts"
   git branch -M main
   git remote add origin https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot.git
   git push -u origin main
   ```

### If Git is already installed:

```bash
cd C:\Projects\yandex-music-podcastr-parser
git init
git add .
git commit -m "Initial commit: VK bot for Yandex Music podcasts 🎙"
git branch -M main
git remote add origin https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot.git
git push -u origin main
```

## After Publishing

1. The repository URL is already set to: `https://github.com/alexsoftware-java/yandex-podcast-downloader-vkbot`

2. Add repository description on GitHub

3. Create first release:
   - Go to **Releases** → **Create a new release**
   - Tag version: `v1.0.0`
   - Release title: `Version 1.0.0`
   - Description: Use CHANGELOG.md

## Done! 🎉

Your bot is published on GitHub!
