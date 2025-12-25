# -*- coding: utf-8 -*-
"""Keep-alive system for Render free tier"""

import asyncio
import logging
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)

class KeepAlive:
    """Keep-alive system to prevent Render from sleeping"""
    
    def __init__(self, url: str, interval: int = 840):
        """
        Initialize keep-alive system
        
        Args:
            url: The URL to ping (your Render app URL)
            interval: Ping interval in seconds (default: 840 = 14 minutes)
        """
        self.url = url
        self.interval = interval
        self.running = False
        self.task = None
    
    async def ping(self):
        """Ping the server to keep it alive"""
        try:
            async with aiohttp.ClientSession() as session:
                # Ping root URL since /health endpoint is not available
                async with session.get(self.url, timeout=10) as response:
                    if response.status in [200, 404]:  # 404 is ok, means server is up
                        logger.info(f"✅ Keep-alive ping successful at {datetime.now()}")
                    else:
                        logger.warning(f"⚠️ Keep-alive ping returned status {response.status}")
        except Exception as e:
            logger.error(f"❌ Keep-alive ping failed: {e}")
    
    async def run(self):
        """Run the keep-alive loop"""
        self.running = True
        logger.info(f"🔄 Keep-alive started (pinging every {self.interval} seconds)")
        
        while self.running:
            await asyncio.sleep(self.interval)
            if self.running:  # Check again after sleep
                await self.ping()
    
    async def start(self, application=None):
        """Start the keep-alive system"""
        if not self.task or self.task.done():
            self.task = asyncio.create_task(self.run())
            logger.info("🚀 Keep-alive system started")
    
    def stop(self):
        """Stop the keep-alive system"""
        self.running = False
        if self.task and not self.task.done():
            self.task.cancel()
            logger.info("🛑 Keep-alive system stopped")
