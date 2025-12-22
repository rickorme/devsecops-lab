FROM python:3.13-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system tools and clean up
RUN apt-get update && apt-get install -y \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/devsecops-lab

# We install directly from pyproject.toml
# 1. Upgrade build tools
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 2. Copy ONLY the dependency definition
# This allows Docker to cache the 'pip install' layer
COPY pyproject.toml .

# 3. Install dependencies only
# We use --no-root (if using poetry) or just install the dependencies
# Since you're using standard pip, we install the requirements defined in the toml
RUN pip install --no-cache-dir .

# 4. Bake Playwright into the image
RUN python -m playwright install --with-deps

# No COPY . . needed
# No CMD needed (VS Code handles the startup)