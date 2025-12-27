# Use the official Microsoft Playwright Python image
# It includes Python, Pip, and all Browser binaries pre-installed.
# Check https://mcr.microsoft.com/en-us/product/playwright/python/tags for versions
FROM mcr.microsoft.com/playwright/python:v1.56.0-noble

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspaces/devsecops-lab

# 1. Install Node.js and Newman
# Since we need Newman for the pipeline, we install it globally here.
# The base image is Ubuntu-based (Jammy), so we can use standard commands.
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g newman \
    && rm -rf /var/lib/apt/lists/*

# 2. Python Setup
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 3. Project Dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Note: We removed 'python -m playwright install' because 
# the base image already has the browsers!