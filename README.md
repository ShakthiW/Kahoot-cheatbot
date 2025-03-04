# Project Name

Brief description of your project - what it does and its main purpose.

## Features

- Cheat Kahoot questions with AI
- Get the answers to any type of question with AI
- Use the AI to help you study for any subject

## Prerequisites

- Python 3.x
- Other dependencies

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/project-name.git
cd project-name
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.sample`:

```bash
cp .env.sample .env
```

## Configuration

Update the `.env` file with your configuration:

```bash
OPENAI_API_KEY="Your OpenAI API Key"
```

## Usage

```bash
python main.py
```

## Project Structure

project-name/
├── README.md
├── requirements.txt
├── .env.sample
├── .env
└── src/
└── main.py

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
