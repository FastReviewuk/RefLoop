import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                free_submissions_available INTEGER DEFAULT 0,
                total_verified_claims INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Referral links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_links (
                id SERIAL PRIMARY KEY,
                referrer_user_id BIGINT NOT NULL,
                category TEXT NOT NULL,
                service_name TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                max_claims INTEGER NOT NULL,
                current_claims INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_user_id) REFERENCES users(user_id)
            )
        """)
        
        # Migrate old column name if exists
        cursor.execute("""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='referral_links' AND column_name='used_claims'
                ) THEN
                    ALTER TABLE referral_links RENAME COLUMN used_claims TO current_claims;
                END IF;
            END $$;
        """)
        
        # Claims table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id SERIAL PRIMARY KEY,
                referred_user_id BIGINT NOT NULL,
                link_id INTEGER NOT NULL,
                screenshot_file_id VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                rewarded BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referred_user_id) REFERENCES users(user_id),
                FOREIGN KEY (link_id) REFERENCES referral_links(id),
                UNIQUE(referred_user_id, link_id)
            )
        """)
        
        cursor.close()
        print("Database initialized successfully!")

# User operations
def create_user(user_id: int, username: str):
    """Create a new user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, username)
            VALUES (%s, %s)
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id, username))
        cursor.close()

def get_user(user_id: int):
    """Get user by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user

def update_user_claims(user_id: int):
    """Increment user's verified claims and handle free submission unlock"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            UPDATE users 
            SET total_verified_claims = total_verified_claims + 1
            WHERE user_id = %s
            RETURNING total_verified_claims
        """, (user_id,))
        result = cursor.fetchone()
        total_claims = result['total_verified_claims']
        
        # Grant free submission after 3rd claim
        if total_claims == 3:
            cursor.execute("""
                UPDATE users 
                SET free_submissions_available = free_submissions_available + 1
                WHERE user_id = %s
            """, (user_id,))
        
        cursor.close()
        return total_claims

def use_free_submission(user_id: int):
    """Decrement free submissions counter"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET free_submissions_available = free_submissions_available - 1
            WHERE user_id = %s AND free_submissions_available > 0
        """, (user_id,))
        cursor.close()

# Referral link operations
def create_referral_link(referrer_user_id: int, category: str, service_name: str, url: str, description: str, max_claims: int):
    """Create a new referral link with specified max claims"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO referral_links (referrer_user_id, category, service_name, url, description, max_claims, current_claims)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
            RETURNING id
        """, (referrer_user_id, category, service_name, url, description, max_claims))
        link_id = cursor.fetchone()[0]
        cursor.close()
        return link_id

def get_available_links(category: str = None):
    """Get available referral links (not maxed out)"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        if category:
            cursor.execute("""
                SELECT * FROM referral_links 
                WHERE current_claims < max_claims AND category = %s
                ORDER BY created_at DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM referral_links 
                WHERE current_claims < max_claims
                ORDER BY created_at DESC
            """)
        links = cursor.fetchall()
        cursor.close()
        return links

def get_link_by_id(link_id: int):
    """Get referral link by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM referral_links WHERE id = %s", (link_id,))
        link = cursor.fetchone()
        cursor.close()
        return link

def increment_link_claims(link_id: int):
    """Increment current claims for a link and return updated values"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            UPDATE referral_links 
            SET current_claims = current_claims + 1
            WHERE id = %s
            RETURNING current_claims, max_claims, service_name, referrer_user_id
        """, (link_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

def delete_referral_link(link_id: int):
    """Delete a referral link that has reached its limit"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM referral_links 
            WHERE id = %s
        """, (link_id,))
        cursor.close()

def get_categories():
    """Get all unique categories"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM referral_links ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return categories

# Claim operations
def create_claim(referred_user_id: int, link_id: int, screenshot_file_id: str):
    """Create a new claim"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO claims (referred_user_id, link_id, screenshot_file_id)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (referred_user_id, link_id, screenshot_file_id))
        claim_id = cursor.fetchone()[0]
        cursor.close()
        return claim_id

def get_claim(claim_id: int):
    """Get claim by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM claims WHERE id = %s", (claim_id,))
        claim = cursor.fetchone()
        cursor.close()
        return claim

def approve_claim(claim_id: int):
    """Approve a claim"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE claims 
            SET status = 'approved'
            WHERE id = %s
        """, (claim_id,))
        cursor.close()

def mark_claim_rewarded(claim_id: int):
    """Mark claim as rewarded"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE claims 
            SET rewarded = TRUE
            WHERE id = %s
        """, (claim_id,))
        cursor.close()

def reject_claim(claim_id: int):
    """Reject a claim"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE claims 
            SET status = 'rejected'
            WHERE id = %s
        """, (claim_id,))
        cursor.close()

def check_duplicate_claim(user_id: int, link_id: int):
    """Check if user already claimed this link"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM claims 
            WHERE referred_user_id = %s AND link_id = %s
        """, (user_id, link_id))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
