# Tistory Downloader

Tistory Downloader is a Python script designed to extract and download images from a Tistory blog's RSS feed.

## Disclaimer

The Tistory Downloader, a Python script for educational image extraction, comes with a caution for user discretion. It is intended solely for educational and research purposes, prohibiting alterations, modifications, or commercial use of downloaded images. Users are responsible for ethical and legal compliance, and we disclaim liability for any consequences.

## Getting Started

### Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/taka-wang/tistory-downloader.git
   cd tistory-downloader
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:

   ```bash
   python app.py -i [TISTORY_BLOG_URL] -f [FILTER_DATE] -o [OUTPUT_FOLDER]
   ```

## Options

- `-i`, `--url`: The URL of the Tistory blog's RSS feed.
- `-f`, `--filter`: Filter entries after this date (format: YYYY/MM/DD).
- `-o`, `--output`: The output folder for downloaded images (default: 'images').

## Example

```bash
python tistory_downloader.py -i https://iuedelweiss.tistory.com -f 2023/01/01 -o images

python app.py -i https://onlyiu.tistory.com
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
