@echo off
cls
copy backup.sqlite3 db.sqlite3 /y
python manage.py scan "D:\\"
