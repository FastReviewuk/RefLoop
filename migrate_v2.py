#!/usr/bin/env python3
"""
Migration script for RefLoop Bot v2.0
Renames used_claims to current_claims in referral_links table
"""

import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def migrate():
    """Run migration"""
    print("🔄 Starting migration to v2.0...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check if migration is needed
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='referral_links' AND column_name='used_claims'
        """)
        
        if cursor.fetchone():
            print("  📝 Renaming used_claims to current_claims...")
            cursor.execute("""
                ALTER TABLE referral_links 
                RENAME COLUMN used_claims TO current_claims
            """)
            conn.commit()
            print("  ✅ Column renamed successfully!")
        else:
            print("  ℹ️  Migration already applied or column doesn't exist")
        
        # Verify the change
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='referral_links' AND column_name='current_claims'
        """)
        
        if cursor.fetchone():
            print("  ✅ Verified: current_claims column exists")
        else:
            print("  ❌ Error: current_claims column not found")
            sys.exit(1)
        
        # Show current links
        cursor.execute("""
            SELECT COUNT(*) FROM referral_links
        """)
        count = cursor.fetchone()[0]
        print(f"  📊 Current referral links: {count}")
        
        if count > 0:
            cursor.execute("""
                SELECT 
                    service_name, 
                    current_claims, 
                    max_claims 
                FROM referral_links 
                LIMIT 5
            """)
            print("\n  Sample links:")
            for row in cursor.fetchall():
                print(f"    - {row[0]}: {row[1]}/{row[2]} claims")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("  1. Restart your bot: python bot.py")
        print("  2. Test the new plan selection")
        print("  3. Verify auto-deletion works")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set in environment")
        print("Please set it in your .env file or environment variables")
        sys.exit(1)
    
    print("RefLoop Bot v2.0 Migration")
    print("=" * 50)
    print(f"Database: {DATABASE_URL[:30]}...")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        migrate()
    else:
        print("Migration cancelled")
