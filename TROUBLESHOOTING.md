# 🔧 Troubleshooting Guide

This guide addresses the most common issues when using the Bluesky Disinfo Analyzer and their solutions.

## 🚫 Error 403 - Forbidden

### Symptoms
```
403 on https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts – sleep 1 s (attempt 1)
PermissionError: public Bluesky search blocked this term (403)
```

### Causes
- **Rate Limiting:** Too many requests in a short time
- **IP Blocking:** IP temporarily blocked by the API
- **Content Filters:** Some terms may be automatically blocked

### Solutions
1. **Wait**: Wait 5-10 minutes before trying again
2. **Change hashtag**: Try less controversial terms like "bluesky", "technology"
3. **Reduce frequency**: Avoid running consecutive analyses quickly
4. **Use VPN**: If IP is blocked, try a different IP

### Prevention
- Wait at least 30 seconds between analyses
- Use popular and non-controversial hashtags for testing
- Monitor status on the "🔧 API Status" page

## 🌐 Error 404 - Not Found

### Symptoms
```
404 Client Error: Not Found for url: https://search.bsky.social/search/posts
ConnectionError: All Bluesky API endpoints failed
```

### Causes
- **API unavailable**: Endpoint temporarily down
- **Connectivity issues**: Unstable internet
- **API changes**: Endpoints may have changed

### Solutions
1. **Check internet**: Test other websites to confirm connectivity
2. **Wait**: APIs may be under maintenance
3. **Test connectivity**: Use the "🔧 API Status" page
4. **Try later**: Wait 15-30 minutes

## 🔍 Empty Results

### Symptoms
- "No related hashtags found"
- Empty charts
- Empty user lists

### Causes
- **Very specific hashtag**: Few posts with this hashtag
- **Too restrictive filters**: Settings eliminated all results
- **Non-existent hashtag**: Term never used on Bluesky

### Solutions
1. **Reduce filters**: Lower "minimum count" to 1
2. **Popular hashtags**: Test with "bluesky", "brasil", "news"
3. **Check spelling**: Confirm hashtag is correct
4. **Increase "Top N"**: Configure to show more results

## ⚠️ Timeout Error

### Symptoms
```
requests.exceptions.Timeout: Request timeout
```

### Causes
- **Slow connection**: Unstable internet
- **Overloaded API**: Too many simultaneous requests
- **Large requests**: Too much data being processed

### Solutions
1. **Wait**: Try again in a few minutes
2. **Reduce scope**: Use less ambitious settings
3. **Check internet**: Test connection speed

## 🐛 Import/Module Errors

### Symptoms
```
ModuleNotFoundError: No module named 'streamlit'
ImportError: cannot import name 'extract' from module
```

### Causes
- **Missing dependencies**: Missing packages
- **Incompatible versions**: Version conflicts
- **Corrupted files**: Incomplete downloads

### Solutions
1. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Use virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

3. **Check versions**:
   ```bash
   pip list | grep streamlit
   python --version
   ```

## 📊 Visualization Issues

### Symptoms
- Charts don't appear
- WordCloud errors
- Strange characters

### Causes
- **Visualization dependencies**: Matplotlib/Altair poorly installed
- **Encoding**: Issues with special characters
- **Insufficient data**: Too little data to generate visualizations

### Solutions
1. **Reinstall matplotlib**:
   ```bash
   pip uninstall matplotlib
   pip install matplotlib>=3.8.0
   ```

2. **Check data**: Ensure there's sufficient data
3. **Test with simple data**: Use hashtags known to work

## 🔄 Performance Issues

### Symptoms
- Very slow app
- Freezing
- Insufficient memory

### Causes
- **Too much data**: Very large analyses
- **Cache**: Streamlit cache issues
- **Limited resources**: Insufficient RAM/CPU

### Solutions
1. **Reduce scope**: Analyze less data at a time
2. **Clear cache**:
   ```bash
   streamlit cache clear
   ```
3. **Restart app**: Stop and start again
4. **Monitor resources**: Use task manager

## 📞 How to Report Issues

If no solution worked:

1. **Collect information**:
   - Complete error message
   - Hashtag/URL that caused the problem
   - Settings used
   - Python version (`python --version`)

2. **Test reproduction**:
   - Try to reproduce the error
   - Test with different data
   - Note exact steps

3. **Report on GitHub**:
   - Go to: https://github.com/reichaves/bluesky_analytics/issues
   - Create a new issue
   - Include all collected information

## 🛠️ Useful Debug Commands

### Check installation
```bash
python -c "import streamlit; print(streamlit.__version__)"
python -c "import pandas; print(pandas.__version__)"
python -c "import requests; print(requests.__version__)"
```

### Test connectivity
```bash
curl -I https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts
ping 8.8.8.8
```

### Run with debug
```bash
streamlit run app.py --logger.level debug
```

### Check logs
- Check terminal output
- Look for complete stack traces
- Note error timestamps

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Bluesky API Docs](https://docs.bsky.app/)
- [GitHub Issues](https://github.com/reichaves/bluesky_analytics/issues)
- [Python Requests Docs](https://docs.python-requests.org/)

## 🌐 Common Issues by Region

### Brazil
- **Language issues**: Use Portuguese terms like "brasil", "política"
- **Character encoding**: Ensure UTF-8 support for Portuguese characters
- **Time zones**: API timestamps may be in UTC

### International Users
- **VPN considerations**: Some regions may have different API access
- **Language barriers**: Try English hashtags like "news", "politics"
- **Local hashtags**: Research popular hashtags in your region

## 🚀 Performance Optimization

### For Large Analyses
1. **Batch processing**: Break large requests into smaller chunks
2. **Caching**: Use Streamlit's caching features
3. **Pagination**: Process results in pages
4. **Filtering**: Apply filters early to reduce data volume

### For Slow Connections
1. **Reduce timeouts**: Lower timeout values in requests
2. **Smaller page sizes**: Request fewer items per page
3. **Fallback endpoints**: Use multiple API endpoints
4. **Retry logic**: Implement exponential backoff

## 🔐 API Key and Authentication Issues

### Symptoms
- "Authentication required" errors
- "Invalid credentials" messages
- Persistent 401 errors

### Causes
- **Missing API keys**: Some endpoints may require authentication
- **Expired tokens**: Authentication tokens may have expired
- **Rate limiting**: Exceeded anonymous usage limits

### Solutions
1. **Check API documentation**: Verify if endpoint requires authentication
2. **Use public endpoints**: Stick to publicly available APIs
3. **Contact developers**: Report authentication issues on GitHub

## 🧪 Testing and Validation

### Quick Health Check
Run this simple test to verify your installation:

```python
# test_installation.py
try:
    import streamlit as st
    import pandas as pd
    import requests
    import matplotlib.pyplot as plt
    import altair as alt
    from wordcloud import WordCloud
    print("✅ All dependencies imported successfully")
    
    # Test API connectivity
    response = requests.get("https://httpbin.org/status/200", timeout=5)
    if response.status_code == 200:
        print("✅ Internet connectivity working")
    else:
        print("❌ Internet connectivity issues")
        
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### API Endpoint Testing
Test individual endpoints to identify which ones are working:

```python
# test_endpoints.py
import requests

endpoints = [
    "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
    "https://bsky.social/xrpc/app.bsky.feed.searchPosts", 
    "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{endpoint}?q=test&limit=1", timeout=10)
        print(f"✅ {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint}: {str(e)}")
```

## 📋 Environment Setup Checklist

Before reporting issues, verify:

- [ ] Python version 3.8+ (`python --version`)
- [ ] All dependencies installed (`pip list`)
- [ ] Internet connectivity working
- [ ] No firewall blocking requests
- [ ] Sufficient disk space for cache
- [ ] No antivirus blocking Python/Streamlit

## 🎯 Specific Error Solutions

### "SSL Certificate Verify Failed"
```bash
# For macOS
/Applications/Python\ 3.x/Install\ Certificates.command

# For all systems
pip install --upgrade certifi
```

### "Permission Denied" on Windows
```bash
# Run as administrator or use:
pip install --user -r requirements.txt
```

### "Port already in use"
```bash
# Kill existing Streamlit processes
pkill -f streamlit
# Or use different port
streamlit run app.py --server.port 8502
```

### Memory Issues on Large Datasets
```python
# Add to your script
import gc
gc.collect()  # Force garbage collection

# Use data chunking
def process_in_chunks(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]
```

## 🔄 Recovery Procedures

### If App Becomes Unresponsive
1. **Force quit**: Ctrl+C in terminal
2. **Clear cache**: `streamlit cache clear`
3. **Restart fresh**: `streamlit run app.py`
4. **Check resources**: Monitor CPU/RAM usage

### If Data Gets Corrupted
1. **Clear browser cache**: Hard refresh (Ctrl+F5)
2. **Reset Streamlit session**: Refresh the page
3. **Delete temp files**: Clear system temp directory
4. **Reinstall dependencies**: Fresh pip install

## 📞 Getting Help

### Before Asking for Help
1. **Read this guide completely**
2. **Check existing GitHub issues**
3. **Try the suggested solutions**
4. **Gather error logs and system info**

### When Creating an Issue
Include:
- **Environment**: OS, Python version, dependency versions
- **Error message**: Complete stack trace
- **Steps to reproduce**: Exact sequence that caused the error
- **Expected vs actual**: What should happen vs what happens
- **Screenshots**: If UI-related
- **Log files**: Any relevant log output

### Community Resources
- **GitHub Discussions**: For general questions
- **Issues**: For bug reports
- **Wiki**: For documentation
- **Streamlit Community**: For Streamlit-specific issues

## 🛡️ Security Considerations

### Data Privacy
- **No personal data**: App only uses public API data
- **Local processing**: All analysis happens locally
- **No data storage**: Results not permanently stored
- **API compliance**: Follows Bluesky API terms of service

### Safe Usage
- **Rate limiting**: Respect API limits to avoid IP blocking
- **Terms compliance**: Follow platform terms of service
- **Ethical research**: Use responsibly for legitimate research
- **Data attribution**: Credit sources appropriately

## 🚀 Advanced Troubleshooting

### Docker Deployment Issues
```dockerfile
# If using Docker, ensure proper setup
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### Cloud Deployment
- **Streamlit Cloud**: Check resource limits
- **Heroku**: Ensure proper Procfile
- **AWS/GCP**: Verify network and security settings
- **Resource limits**: Monitor memory and CPU usage

### Load Testing
If planning high-volume usage:
```python
import asyncio
import aiohttp

async def stress_test():
    # Test concurrent requests
    pass
```

## 📈 Monitoring and Logging

### Enable Detailed Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bluesky_analyzer.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring
```python
import time
import psutil

def monitor_performance():
    start_time = time.time()
    memory_before = psutil.virtual_memory().percent
    
    # Your code here
    
    end_time = time.time()
    memory_after = psutil.virtual_memory().percent
    
    print(f"Execution time: {end_time - start_time:.2f}s")
    print(f"Memory usage: {memory_after - memory_before:.1f}%")
```

---

💡 **Remember**: This is an open-source project developed during a hackathon. Some issues are expected, and the community's help in identifying and fixing them is valuable!

🤝 **Contributing**: If you solve an issue not covered here, please consider contributing the solution back to this guide.

📚 **Keep Learning**: The Bluesky API and ecosystem are rapidly evolving. Stay updated with the latest documentation and community discussions.
