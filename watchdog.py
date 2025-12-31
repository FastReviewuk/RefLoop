# -*- coding: utf-8 -*-
import subprocess
import time
import logging
import sys
from datetime import datetime
import watchdog_config as config

logging.basicConfig(
    format='%(asctime)s - WATCHDOG - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

def run_bot():
    """Run the bot process and monitor it"""
    restart_count = 0
    restart_times = []
    
    while True:
        try:
            logger.info("=" * 70)
            logger.info(f"🚀 Starting bot process (restart #{restart_count + 1})")
            logger.info("=" * 70)
            
            # Start the bot process
            process = subprocess.Popen(
                [sys.executable, 'bot.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Monitor the process output
            while True:
                line = process.stdout.readline()
                if line:
                    print(line.rstrip())
                    if config.VERBOSE_LOGGING:
                        logger.info(f"BOT: {line.rstrip()}")
                
                # Check if process is still running
                if process.poll() is not None:
                    exit_code = process.returncode
                    logger.warning(f"⚠️  Bot process exited with code {exit_code}")
                    break
            
            # Process crashed, prepare for restart
            restart_count += 1
            restart_times.append(datetime.now())
            
            # Clean up old restart times (older than 1 hour)
            restart_times = [t for t in restart_times if (datetime.now() - t).total_seconds() < 3600]
            
            # Check if we're restarting too frequently
            if len(restart_times) > config.MAX_RESTARTS_PER_HOUR:
                logger.error(f"❌ Too many restarts ({len(restart_times)}) in the last hour!")
                logger.error(f"⏸️  Waiting 5 minutes before next restart attempt...")
                time.sleep(300)
            else:
                # Calculate wait time with exponential backoff
                wait_time = min(
                    config.MAX_RESTART_WAIT,
                    config.INITIAL_RESTART_WAIT * (config.BACKOFF_MULTIPLIER ** (restart_count - 1))
                )
                wait_time = int(wait_time)
                logger.info(f"⏳ Waiting {wait_time} seconds before restart...")
                time.sleep(wait_time)
        
        except KeyboardInterrupt:
            logger.info("🛑 Watchdog interrupted by user")
            if 'process' in locals():
                process.terminate()
            break
        except Exception as e:
            logger.error(f"❌ Watchdog error: {e}", exc_info=True)
            time.sleep(10)

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🔍 WATCHDOG STARTED - Monitoring bot process")
    logger.info(f"Max restarts per hour: {config.MAX_RESTARTS_PER_HOUR}")
    logger.info(f"Initial restart wait: {config.INITIAL_RESTART_WAIT}s")
    logger.info(f"Max restart wait: {config.MAX_RESTART_WAIT}s")
    logger.info("=" * 70)
    run_bot()
