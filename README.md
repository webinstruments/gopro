# Install
```bash
poetry env use python3.9
poetry install
```

# How to
0) rename _config.py to config.py
1) login to your go pro lib
2) press f12
3) take the `Authorization: Bearer ...` header from any request and set `bearer_token` variable
4) take any media request and increase page size (use firefox to manipulate the request),
put the whole response in `search_response`.
5) select a folder where your videos should be stored. Media will be stored in the folder with this format: `{storage_path}/{ddmmYYYY}/media_name.ext`. Already downloaded media will be skipped
6) `poetry python gopro/main.py`