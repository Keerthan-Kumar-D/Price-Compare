@echo off
echo ============================================================
echo    MYNTRA SELENIUM SCRAPER - SERVER STARTER
echo ============================================================
echo.
echo Starting server...
echo Server will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
python myntra_selenium_server.py

pause
