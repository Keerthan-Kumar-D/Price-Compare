@echo off
echo ============================================================
echo    MYNTRA SELENIUM SCRAPER - TEST CLIENT
echo ============================================================
echo.
echo Make sure the server is running first!
echo (Run start_server.bat in another window)
echo.
echo Press any key to start the test client...
pause > nul
echo.
echo Running test client...
echo ============================================================
echo.

cd /d "%~dp0"
python test_selenium_client.py

echo.
echo ============================================================
echo Test completed! Check the JSON files for results.
echo ============================================================
pause
