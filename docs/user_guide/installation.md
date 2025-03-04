# Installation Guide

This guide will walk you through the process of setting up the NCAA March Madness Predictor project on your local machine.

## Prerequisites

Before you begin, make sure you have the following installed:

- **Python 3.10 or higher**: Required for all project components
- **Git**: For cloning the repository
- **pip or uv**: For package management
- **7GB+ disk space**: Required for storing the raw and processed data

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/march_madness.git
cd march_madness
```

## Step 2: Create a Virtual Environment

We recommend using a virtual environment to avoid conflicts with other Python packages.

### Using venv (Standard Library)

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

### Using conda

```bash
conda create -n march_madness python=3.10
conda activate march_madness
```

### Using uv (Recommended)

```bash
uv venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Using pip
pip install -r requirements.txt

# OR using uv (faster)
uv pip install -r requirements.txt
```

## Step 4: Verify Installation

Run the test script to verify that everything is installed correctly:

```bash
python tests/test_installation.py
```

You should see the message "Installation successful!" if everything is set up correctly.

## Step 5: Download Initial Data

To download the initial dataset (this may take some time depending on your internet connection):

```bash
python -m src.data.loader --years 2022 2023 2024
```

This will download data for the 2022, 2023, and 2024 NCAA basketball seasons.

## Troubleshooting

### Common Issues

1. **Missing dependencies**: If you encounter errors about missing modules, try reinstalling the requirements:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

2. **Data download issues**: If data download fails, check your internet connection and try again. The script will resume from where it left off.

3. **Memory issues during data processing**: For systems with limited RAM, try processing one season at a time:
   ```bash
   python -m src.data.loader --years 2024
   python -m src.pipeline.data --seasons 2024
   ```

### Getting Help

If you encounter any issues not covered here, please open an issue on the project's GitHub repository or contact the project maintainers. 