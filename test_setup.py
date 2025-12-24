#!/usr/bin/env python3
"""
Test script to verify RefLoop bot setup
Run this before deploying to catch configuration issues
"""

import os
import sys
from dotenv import load_dotenv

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("🔍 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = ['BOT_TOKEN', 'DATABASE_URL', 'ADMIN_USER_IDS']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"  ❌ {var}: Not set")
        else:
            # Mask sensitive data
            if var == 'BOT_TOKEN':
                masked = value[:10] + '...' + value[-10:] if len(value) > 20 else '***'
                print(f"  ✅ {var}: {masked}")
            elif var == 'DATABASE_URL':
                print(f"  ✅ {var}: {value[:20]}...")
            else:
                print(f"  ✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment")
        return False
    
    print("✅ All environment variables are set!\n")
    return True

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        print(f"  ✅ Connected to PostgreSQL")
        print(f"  ℹ️  Version: {version[:50]}...")
        print("✅ Database connection successful!\n")
        return True
        
    except ImportError:
        print("  ❌ psycopg2 not installed")
        print("  Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print("  Check your DATABASE_URL")
        return False

def test_bot_token():
    """Test if bot token is valid"""
    print("🔍 Testing bot token...")
    
    try:
        import asyncio
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        
        async def check_token():
            bot = Bot(token=bot_token)
            me = await bot.get_me()
            return me
        
        me = asyncio.run(check_token())
        print(f"  ✅ Bot token is valid!")
        print(f"  ℹ️  Bot name: {me.first_name}")
        print(f"  ℹ️  Bot username: @{me.username}")
        print("✅ Bot token test successful!\n")
        return True
        
    except ImportError:
        print("  ❌ python-telegram-bot not installed")
        print("  Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"  ❌ Token validation failed: {e}")
        print("  Check your BOT_TOKEN")
        return False

def test_admin_ids():
    """Test if admin IDs are valid"""
    print("🔍 Testing admin user IDs...")
    
    admin_ids = os.getenv('ADMIN_USER_IDS', '')
    
    if not admin_ids:
        print("  ❌ No admin IDs set")
        return False
    
    try:
        ids = [int(id.strip()) for id in admin_ids.split(',') if id.strip()]
        print(f"  ✅ Found {len(ids)} admin ID(s)")
        for i, admin_id in enumerate(ids, 1):
            print(f"  ℹ️  Admin {i}: {admin_id}")
        print("✅ Admin IDs are valid!\n")
        return True
    except ValueError:
        print("  ❌ Invalid admin ID format")
        print("  Should be comma-separated numbers: 123456789,987654321")
        return False

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing package imports...")
    
    packages = [
        ('telegram', 'python-telegram-bot'),
        ('psycopg2', 'psycopg2-binary'),
        ('dotenv', 'python-dotenv'),
    ]
    
    all_ok = True
    for module, package in packages:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            all_ok = False
    
    if all_ok:
        print("✅ All packages are installed!\n")
    else:
        print("\n❌ Some packages are missing")
        print("Run: pip install -r requirements.txt\n")
    
    return all_ok

def test_database_schema():
    """Test if database tables can be created"""
    print("🔍 Testing database schema...")
    
    try:
        import database as db
        db.init_database()
        print("  ✅ Database tables created/verified")
        print("✅ Database schema test successful!\n")
        return True
    except Exception as e:
        print(f"  ❌ Schema creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("RefLoop Bot - Setup Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Package Imports", test_imports),
        ("Database Connection", test_database_connection),
        ("Database Schema", test_database_schema),
        ("Bot Token", test_bot_token),
        ("Admin IDs", test_admin_ids),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your bot is ready to deploy!")
        print("\nNext steps:")
        print("1. Run: python bot.py")
        print("2. Open Telegram and search for your bot")
        print("3. Send /start to test")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
