# jmci

A high-level wrapper around `jmcomic` that provides a fluent search and download API plus a simple CLI.

`jmci` keeps the most common album search and download workflows, while hiding lower-level details of `jmcomic`.

## Features

- Fluent, chainable search API for albums
- Flexible download API with folder, PDF, and ZIP export formats
- Built-in CLI: `jmci search` and `jmci download`
- Logging and progress output with rich formatting
- Minimal wrapper focused on the most useful `jmcomic` workflows

## Install

Requires Python 3.12+

```bash
pip install jmci
```

Or with `uv`:

```bash
uv add jmci
```

## Quick Start

### Python API

```python
from jmci import Download, Search, SearchType, ExportFormat, enable_logging

# Enable rich logging
enable_logging(True)

# Search albums
results = (
    Search("keyword")
    .searching(SearchType.author)
    .pages([1, 2])
    .order_by("score")
    .filter_time("week")
    .category("doujin")
    .sub_category("chinese")
    .process()
)

for item in results:
    print(item.id, item.title)

# Download one or more albums
(
    Download([123456, 789012])
    .export_format(ExportFormat.folder | ExportFormat.pdf)
    .directory("./downloads")
    .jpg(True)
    .pictures(30)
    .process()
)
```

### CLI

```bash
jmci search "keyword" --search-type author --order-by score --pages 1 2 --filter-time week
jmci download 123456 --directory ./downloads --export-format pdf zip --jpg
jmci download 123456 --cover
```

## API Overview

### Search

Use `Search` to build a search request and execute it with `process()`.

```python
from jmci import Search, SearchType, OrderBy, FilterTime, Category, SubCategory

results = (
    Search("keyword")
    .searching(SearchType.tag)
    .pages([1])
    .order_by(OrderBy.latest)
    .filter_time(FilterTime.all)
    .category(Category.all)
    .sub_category(SubCategory.none)
    .process()
)
```

Search supports:

- `searching(type)` — choose `SearchType` (all, work, author, tag, actor)
- `pages(pages)` — search pagination pages
- `keyword(keyword)` — update the search keyword
- `order_by(order_by)` — ordering strategy
- `filter_time(filter_time)` — publication time filter
- `category(category)` — main category filter
- `sub_category(sub_category)` — subcategory filter
- `process()` — execute the search and return results
- `process_select(converter)` — convert results while processing
- `where(filter)`, `sort(key)`, `reverse()`, `join(...)` — filter and transform results

`SearchResult` objects expose:

- `id`
- `title`
- `tags`

### Download

Use `Download` to download albums with configurable export options.

```python
from jmci import Download, ExportFormat

(
    Download([123456])
    .directory("./downloads")
    .export_format(ExportFormat.folder | ExportFormat.zip)
    .jpg(True)
    .pictures(20)
    .process()
)
```

Download supports:

- `downloading(album_ids)` — replace the album list
- `add(id)`, `remove(id)`, `pop(index)`, `insert(index, id)`, `extend(ids)` — manage album IDs
- `export_format(format)` — set output format
- `add_export_format(format)` / `remove_export_format(format)` — modify format set
- `directory(directory)` — output directory
- `jpg(convert_to_jpg=True)` — convert pictures to JPG
- `pictures(pictures)` — limit download concurrency per album
- `process()` — perform full album download and export
- `process_download_cover()` — download album cover images only

Supported export formats:

- `ExportFormat.folder`
- `ExportFormat.pdf`
- `ExportFormat.zip`

Formats can be combined using bitwise OR.

### Logging

`jmci` exposes `enable_logging()` to toggle rich logging output.

```python
from jmci import enable_logging
enable_logging(True)
```

## Documentation

Documentation is available under `docs/source` and can be built with Sphinx:

```bash
uv run sphinx-build -b html docs/source docs/build
```

## Dependencies

`jmci` is a lightweight wrapper and depends on:

- `jmcomic`
- `rich`
- `typer`
- `beartype`
- `img2pdf`

## License

MIT License
