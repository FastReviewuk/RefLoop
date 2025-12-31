# -*- coding: utf-8 -*-
"""
Watchdog Configuration
Controls how the bot watchdog behaves
"""

# Maximum number of restarts allowed per hour
MAX_RESTARTS_PER_HOUR = 10

# Initial wait time before first restart (seconds)
INITIAL_RESTART_WAIT = 5

# Maximum wait time between restarts (seconds)
MAX_RESTART_WAIT = 30

# Exponential backoff multiplier
BACKOFF_MULTIPLIER = 1.5

# Enable detailed logging
VERBOSE_LOGGING = True

# Log file location
LOG_FILE = 'watchdog.log'

# Health check interval (seconds) - how often to check if bot is responsive
HEALTH_CHECK_INTERVAL = 60

# Timeout for health check (seconds)
HEALTH_CHECK_TIMEOUT = 10
