# NBA Analytics Bot

The **NBA Analytics Bot** is a Python-based project that leverages the [NBA API](https://github.com/swar/nba_api) to generate insightful reports and analytics for NBA games. It includes features such as daily reports, top player performances, team stats, and shooting efficiency analysis.

---

## Features

- **Daily Reports**:
  - Standout player performances.
  - Game trends (largest blowouts, closest games).
  - Young players watch (players aged 21 or younger).
  - Team stats sorted by wins.
  - Shooting efficiency by zone.

- **Top Performances**:
  - Fetches the top 10 player performances for games played today or yesterday.
  - Calculates a performance score based on points, rebounds, assists, steals, and blocks.

- **Customizable Analytics**:
  - Easily extendable to include additional metrics or insights.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (`venv`) for dependency management

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/nba-analytics-bot.git
   cd nba-analytics-bot

Create and activate a virtual environment:
    Windows (Command Prompt):
        python -m venv .venv
        .\.venv\Scripts\activate

    Windows (PowerShell):
        python -m venv .venv
        .\.venv\Scripts\Activate.ps1

    Mac/Linux:
        python3 -m venv .venv
        source .venv/bin/activate

Install dependencies:
    pip install -r requirements.txt



Dependencies
    nba_api: Python client for accessing NBA stats.
    pandas: Data analysis and manipulation library.


Acknowledgments:
NBA API for providing access to NBA stats.
The Python community for their amazing libraries and tools.

