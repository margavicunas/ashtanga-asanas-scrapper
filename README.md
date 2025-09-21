# Ashtanga Primary Series Scraper 🧘‍♀️

A Python tool that not only collects asana images from the Ashtanga Yoga Primary Series but also helps you find similar asanas by name! Specially useful for studying the sequence offline.

## Purpose

This project makes learning and referencing Ashtanga Primary Series easier by:
- Creating a structured dataset of asanas with their images
- Finding similar asanas to help understand pose relationships
- Making it simple to study the sequence offline
- Providing a local backup of asana references

## Features

- 📸 Downloads all asana images from the primary series
- 🔄 Processes asanas to find similar asanas
- 📝 Creates structured JSON files with asana details
- 🛠️ Includes proper error handling and logging
- 🚀 Uses parallel processing for faster downloads

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/ashtanga-scrapper.git
cd ashtanga-scrapper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The tool has two main commands: `scrape` and `process`.

### Scraping Asanas

To download all asana images and create the initial dataset:
```bash
python main.py scrape [--output-dir data/asanas] [--max-workers 4]
```

Options:
- `--output-dir`: Where to save images and data (default: data/asanas)
- `--max-workers`: Number of parallel downloads (default: 4)

### Processing Asanas

To analyze asanas and find similar asanas:
```bash
python main.py process [--input_file data/asanas/asanas.json] [--output-file output.json] [--max-similar 4]
```

Options:
- `--input_file`: Path to the scraped asanas JSON (default: data/asanas/asanas.json)
- `--output-file`: Where to save processed results (default: adds '_processed' suffix to input file)
- `--max-similar`: Maximum number of similar asanas to find (default: 4)

### Output Format

The scraper generates an `asanas.json` file:
```json
[
  {
    "id": "asana-name",
    "name": "Asana Name",
    "img": "/path/to/image.png"
  }
]
```

After processing, you'll get an enhanced `asanas_processed.json` with similar asanas!

## Development

This project uses:
- `mypy` for type checking
- `black` for code formatting
- Proper logging for debugging

To format code:
```bash
black .
```

To run type checking:
```bash
mypy .
```

## Credits

All asana images and references are sourced from [Devvrat Yoga](https://www.devvratyoga.com/learning-resources/ashtanga-yoga-asanas-with-names-images/). Their website provides excellent resources for yoga practitioners. Please visit their website for comprehensive yoga learning materials.

## License

This project is for educational purasanas only. All asana images belong to their respective owners.