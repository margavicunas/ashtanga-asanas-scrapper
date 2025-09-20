# Ashtanga Primary Series Scraper 🧘‍♀️

A Python scraper that collects and organizes images and names of asanas from the Ashtanga Yoga Primary Series. This tool helps practitioners and teachers easily access a comprehensive collection of asana references.

## Purpose

This project was created to compile a structured dataset of Ashtanga Primary Series asanas, making it easier to:
- Reference asana names and their corresponding images
- Study the sequence offline
- Have a local backup of the asana references

## Features

- Downloads all asana images from the primary series
- Creates a structured JSON file with asana names and image paths
- Handles image format conversion automatically
- Includes proper error handling and logging

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

Run the scraper:
```bash
python main.py
```

The script will:
1. Create an `asanas` directory
2. Download all asana images
3. Generate an `asanas.json` file with the following structure:
```json
[
  {
    "id": "asana-name",
    "name": "Asana Name",
    "img": "/path/to/image.png"
  }
]
```

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

This project is for educational purposes only. All asana images belong to their respective owners.
