@echo off
cd /d "c:/Users/fzhan/Documents/GitHub/stock_charts"
C:/Users/fzhan/miniconda3/envs/invest/python.exe  eod_scraper.py
if %ERRORLEVEL% EQU 0 (
    echo Script ran successfully at %DATE% %TIME% >> success.log
) else (
    echo Script failed at %DATE% %TIME% >> error.log
) 