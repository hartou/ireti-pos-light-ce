# Release Notes - v0.0.2 (Container Fix Release)

**Release Date:** August 17, 2025
**Type:** Patch Release

## 🐛 Bug Fixes

### Docker Container Startup Issue
- **Fixed:** Container startup error `/bin/sh: 1: [sh,: not found` 
- **Root Cause:** Malformed multi-line CMD instruction with improper shell escaping
- **Solution:** Replaced with proper startup script using Docker heredoc syntax
- **Impact:** Docker containers now start reliably without shell parsing errors

## 🔧 Improvements

### Container Reliability
- **Enhanced:** Startup script with better error handling and logging
- **Added:** Clear connection information display on container startup
- **Improved:** Superuser creation process with proper error handling
- **Fixed:** Container shutdown process using `exec` for clean process replacement

### Development Experience
- **Better:** More informative startup messages showing database configuration
- **Cleaner:** Proper shell script structure with error handling
- **Reliable:** Consistent container behavior across different Docker environments

## 📋 Migration Notes

### For Existing Users
- **Recommendation:** Update to v0.0.2 for reliable container startup
- **Action Required:** Pull new image: `docker pull ghcr.io/hartou/ireti-pos-light:latest`
- **Backward Compatible:** No breaking changes, direct drop-in replacement

### Docker Commands
```bash
# Updated quick start
docker pull ghcr.io/hartou/ireti-pos-light:latest
docker run -p 8000:8000 -e DJANGO_SUPERUSER_USERNAME=admin -e DJANGO_SUPERUSER_PASSWORD=Admin123! ghcr.io/hartou/ireti-pos-light:latest
```

## ✅ Verification

The following scenarios have been tested and verified:
- ✅ Container starts without shell parsing errors
- ✅ Django application loads correctly
- ✅ Database migrations run successfully  
- ✅ Superuser creation works with environment variables
- ✅ PWA features function properly
- ✅ All static assets serve correctly

## 🔄 What's Next

This patch release ensures reliable Docker container deployment. The next release (v0.0.3) will focus on:
- Enhanced monitoring and health checks
- Production optimization improvements
- Additional deployment documentation

---

**Important:** This is a critical patch for Docker deployment. All users running v0.0.1 containers should update to v0.0.2 for reliable operation.
