# datamanager.py
"""
🎮 SOCCERFORUM SUPER BOT - Data Manager
Database operations and data management
"""

import logging
import sqlite3
from typing import Dict, List, Any, Optional
from config import Config


class SuperDatabase:
    def __init__(self, db_path=Config.DATABASE_PATH):
        self.db_path = db_path
        self.initialize_database()

    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_database(self):
        """Initialize all database tables"""
        tables = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                role TEXT DEFAULT 'member',
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                threads_created INTEGER DEFAULT 0,
                replies_posted INTEGER DEFAULT 0,
                tournaments_joined INTEGER DEFAULT 0,
                reputation INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Forums table
            """
            CREATE TABLE IF NOT EXISTS forums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                category TEXT,
                icon TEXT DEFAULT '💬',
                color TEXT DEFAULT '#3498db',
                thread_count INTEGER DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                is_featured BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Tournaments table
            """
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                game_version TEXT,
                max_teams INTEGER,
                description TEXT,
                creator_id INTEGER,
                status TEXT DEFAULT 'pending',
                current_teams INTEGER DEFAULT 0,
                prize_pool TEXT DEFAULT 'Glory',
                rules TEXT,
                banner_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (creator_id) REFERENCES users (telegram_id)
            )
            """,
            
            # Tournament participants
            """
            CREATE TABLE IF NOT EXISTS tournament_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_id INTEGER,
                user_id INTEGER,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (tournament_id) REFERENCES tournaments (id),
                FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                UNIQUE(tournament_id, user_id)
            )
            """,
            
            # Threads table
            """
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                forum_id INTEGER,
                creator_id INTEGER,
                reply_count INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                is_pinned BOOLEAN DEFAULT 0,
                is_locked BOOLEAN DEFAULT 0,
                last_reply_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (forum_id) REFERENCES forums (id),
                FOREIGN KEY (creator_id) REFERENCES users (telegram_id)
            )
            """,
            
            # Replies table
            """
            CREATE TABLE IF NOT EXISTS replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                thread_id INTEGER,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES threads (id),
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
            """,
            
            # Badges table
            """
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT 'default'
            )
            """,
            
            # User badges
            """
            CREATE TABLE IF NOT EXISTS user_badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                badge_name TEXT,
                awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
            """,
            
            # User follows
            """
            CREATE TABLE IF NOT EXISTS user_follows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER,
                followed_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users (telegram_id),
                FOREIGN KEY (followed_id) REFERENCES users (telegram_id),
                UNIQUE(follower_id, followed_id)
            )
            """,
            
            # Forum follows
            """
            CREATE TABLE IF NOT EXISTS forum_follows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                forum_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id),
                FOREIGN KEY (forum_id) REFERENCES forums (id),
                UNIQUE(user_id, forum_id)
            )
            """,
            
            # User stats for quick access
            """
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                post_count INTEGER DEFAULT 0,
                badge_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0,
                follower_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
            """
        ]
        
        try:
            with self.get_connection() as conn:
                for table_sql in tables:
                    conn.execute(table_sql)
                
                # Insert default data
                self.insert_default_data(conn)
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")

    def insert_default_data(self, conn):
        """Insert default forums and badges"""
        # Default forums
        if conn.execute("SELECT COUNT(*) FROM forums").fetchone()[0] == 0:
            default_forums = [
                ('FIFA 14', 'fifa14', 'Classic FIFA 14 discussions and tournaments', 'fifa', '🎮', '#e74c3c', 1),
                ('FIFA Modern', 'fifa-modern', 'FIFA 15+ and latest versions', 'fifa', '⚽', '#2ecc71', 0),
                ('eFootball', 'efootball', 'eFootball 2025 and PES series', 'efootball', '🌟', '#9b59b6', 1),
                ('Training Ground', 'training', 'Tips, tricks and gameplay guides', 'guides', '🏋️', '#f39c12', 0),
                ('Tournament Hub', 'tournaments', 'Competitive tournaments and events', 'competitive', '🏆', '#e67e22', 1)
            ]
            
            conn.executemany(
                "INSERT INTO forums (name, slug, description, category, icon, color, is_featured) VALUES (?, ?, ?, ?, ?, ?, ?)",
                default_forums
            )

        # Default badges
        if conn.execute("SELECT COUNT(*) FROM badges").fetchone()[0] == 0:
            default_badges = [
                ('Tournament Champion', 'Win a tournament', 'gold'),
                ('Active Member', 'Post 50+ replies', 'silver'),
                ('Forum Expert', 'Create 10+ threads', 'bronze'),
                ('Community Helper', 'Help other members', 'blue'),
                ('Content Creator', 'Create valuable content', 'purple'),
                ('Social Butterfly', 'Follow 20 users', 'pink')
            ]
            
            conn.executemany(
                "INSERT INTO badges (name, description, color) VALUES (?, ?, ?)",
                default_badges
            )

    # ==================== USER MANAGEMENT ====================
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user with combined stats"""
        try:
            with self.get_connection() as conn:
                user = conn.execute(
                    "SELECT u.*, us.post_count, us.badge_count, us.following_count, us.follower_count "
                    "FROM users u LEFT JOIN user_stats us ON u.telegram_id = us.user_id "
                    "WHERE u.telegram_id = ?", 
                    (user_id,)
                ).fetchone()
                
                if user:
                    return dict(user)
                
                # Create new user
                return self.create_default_user(user_id)
                    
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            return self.create_default_user(user_id)

    def create_default_user(self, user_id: int) -> Dict[str, Any]:
        """Create default user structure"""
        default_user = {
            'telegram_id': user_id,
            'username': f'user_{user_id}',
            'role': 'member',
            'level': 1,
            'experience': 0,
            'threads_created': 0,
            'replies_posted': 0,
            'tournaments_joined': 0,
            'reputation': 0,
            'post_count': 0,
            'badge_count': 0,
            'following_count': 0,
            'follower_count': 0
        }
        
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
                    (user_id, default_user['username'])
                )
                conn.execute(
                    "INSERT OR IGNORE INTO user_stats (user_id) VALUES (?)",
                    (user_id,)
                )
        except Exception as e:
            logging.error(f"Error creating default user: {e}")
            
        return default_user

    def save_user(self, user_id: int, user_data: Dict[str, Any]):
        """Save user data"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO users 
                    (telegram_id, username, full_name, role, level, experience, 
                     threads_created, replies_posted, tournaments_joined, reputation, last_active) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                    (
                        user_id,
                        user_data.get('username'),
                        user_data.get('full_name'),
                        user_data.get('role', 'member'),
                        user_data.get('level', 1),
                        user_data.get('experience', 0),
                        user_data.get('threads_created', 0),
                        user_data.get('replies_posted', 0),
                        user_data.get('tournaments_joined', 0),
                        user_data.get('reputation', 0)
                    )
                )
        except Exception as e:
            logging.error(f"Error saving user {user_id}: {e}")

    def update_user_stats(self, user_id: int, updates: Dict[str, Any]):
        """Update user statistics"""
        try:
            with self.get_connection() as conn:
                # Update users table
                user_fields = ['threads_created', 'replies_posted', 'tournaments_joined', 'reputation', 'experience', 'level']
                user_updates = {k: v for k, v in updates.items() if k in user_fields}
                
                if user_updates:
                    set_clause = ', '.join([f"{k} = {k} + ?" for k in user_updates.keys()])
                    values = list(user_updates.values())
                    conn.execute(f"UPDATE users SET {set_clause} WHERE telegram_id = ?", values + [user_id])
                
                # Update user_stats table
                stats_fields = ['post_count', 'badge_count', 'following_count', 'follower_count']
                stats_updates = {k: v for k, v in updates.items() if k in stats_fields}
                
                if stats_updates:
                    set_clause = ', '.join([f"{k} = {k} + ?" for k in stats_updates.keys()])
                    values = list(stats_updates.values())
                    conn.execute(f"UPDATE user_stats SET {set_clause} WHERE user_id = ?", values + [user_id])
                    
        except Exception as e:
            logging.error(f"Error updating user stats {user_id}: {e}")

    # ==================== TOURNAMENT MANAGEMENT ====================
    def get_tournaments(self, status: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tournaments with filtering"""
        try:
            with self.get_connection() as conn:
                query = "SELECT t.*, u.username as creator_name FROM tournaments t LEFT JOIN users u ON t.creator_id = u.telegram_id"
                params = []
                
                if status:
                    query += " WHERE t.status = ?"
                    params.append(status)
                
                query += " ORDER BY t.created_at DESC LIMIT ?"
                params.append(limit)
                
                tournaments = conn.execute(query, params).fetchall()
                return [dict(tournament) for tournament in tournaments]
        except Exception as e:
            logging.error(f"Error getting tournaments: {e}")
            return []

    def get_tournament(self, tournament_id: int) -> Optional[Dict[str, Any]]:
        """Get specific tournament"""
        try:
            with self.get_connection() as conn:
                tournament = conn.execute(
                    "SELECT t.*, u.username as creator_name FROM tournaments t LEFT JOIN users u ON t.creator_id = u.telegram_id WHERE t.id = ?", 
                    (tournament_id,)
                ).fetchone()
                return dict(tournament) if tournament else None
        except Exception as e:
            logging.error(f"Error getting tournament {tournament_id}: {e}")
            return None

    def create_tournament(self, tournament_data: Dict[str, Any]) -> int:
        """Create new tournament"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO tournaments (name, game_version, max_teams, description, creator_id, status, current_teams, prize_pool) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        tournament_data['name'],
                        tournament_data['game_version'],
                        tournament_data['max_teams'],
                        tournament_data['description'],
                        tournament_data['creator_id'],
                        tournament_data.get('status', 'pending'),
                        tournament_data.get('current_teams', 0),
                        tournament_data.get('prize_pool', 'Glory')
                    )
                )
                return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error creating tournament: {e}")
            return 0

    def join_tournament(self, user_id: int, tournament_id: int) -> bool:
        """Join a tournament"""
        try:
            with self.get_connection() as conn:
                # Check if already joined
                existing = conn.execute(
                    "SELECT id FROM tournament_participants WHERE tournament_id = ? AND user_id = ?",
                    (tournament_id, user_id)
                ).fetchone()
                
                if existing:
                    return False
                
                # Add participant
                conn.execute(
                    "INSERT INTO tournament_participants (tournament_id, user_id) VALUES (?, ?)",
                    (tournament_id, user_id)
                )
                
                # Update counts
                conn.execute(
                    "UPDATE tournaments SET current_teams = current_teams + 1 WHERE id = ?",
                    (tournament_id,)
                )
                
                # Update user stats
                conn.execute(
                    "UPDATE users SET tournaments_joined = tournaments_joined + 1 WHERE telegram_id = ?",
                    (user_id,)
                )
                
                return True
        except Exception as e:
            logging.error(f"Error joining tournament: {e}")
            return False

    def get_tournament_participants(self, tournament_id: int) -> List[int]:
        """Get tournament participants"""
        try:
            with self.get_connection() as conn:
                participants = conn.execute(
                    "SELECT user_id FROM tournament_participants WHERE tournament_id = ?",
                    (tournament_id,)
                ).fetchall()
                return [row[0] for row in participants]
        except Exception as e:
            logging.error(f"Error getting tournament participants: {e}")
            return []

    # ==================== FORUM MANAGEMENT ====================
    def get_forums(self, featured_only: bool = False) -> List[Dict[str, Any]]:
        """Get forums"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM forums"
                if featured_only:
                    query += " WHERE is_featured = 1"
                query += " ORDER BY thread_count DESC"
                
                forums = conn.execute(query).fetchall()
                return [dict(forum) for forum in forums]
        except Exception as e:
            logging.error(f"Error getting forums: {e}")
            return []

    def get_forum(self, forum_id: int) -> Optional[Dict[str, Any]]:
        """Get specific forum"""
        try:
            with self.get_connection() as conn:
                forum = conn.execute(
                    "SELECT * FROM forums WHERE id = ?", 
                    (forum_id,)
                ).fetchone()
                return dict(forum) if forum else None
        except Exception as e:
            logging.error(f"Error getting forum {forum_id}: {e}")
            return None

    def get_threads(self, forum_id: int = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get threads"""
        try:
            with self.get_connection() as conn:
                if forum_id:
                    threads = conn.execute(
                        "SELECT t.*, u.username as creator_name FROM threads t JOIN users u ON t.creator_id = u.telegram_id WHERE t.forum_id = ? ORDER BY t.created_at DESC LIMIT ?",
                        (forum_id, limit)
                    ).fetchall()
                else:
                    threads = conn.execute(
                        "SELECT t.*, u.username as creator_name FROM threads t JOIN users u ON t.creator_id = u.telegram_id ORDER BY t.created_at DESC LIMIT ?",
                        (limit,)
                    ).fetchall()
                
                return [dict(thread) for thread in threads]
        except Exception as e:
            logging.error(f"Error getting threads: {e}")
            return []

    def get_thread(self, thread_id: int) -> Optional[Dict[str, Any]]:
        """Get specific thread"""
        try:
            with self.get_connection() as conn:
                thread = conn.execute(
                    "SELECT t.*, u.username as creator_name, f.name as forum_name FROM threads t JOIN users u ON t.creator_id = u.telegram_id JOIN forums f ON t.forum_id = f.id WHERE t.id = ?", 
                    (thread_id,)
                ).fetchone()
                return dict(thread) if thread else None
        except Exception as e:
            logging.error(f"Error getting thread {thread_id}: {e}")
            return None

    def create_thread(self, thread_data: Dict[str, Any]) -> int:
        """Create new thread"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO threads (title, content, forum_id, creator_id, reply_count, views) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        thread_data['title'],
                        thread_data['content'],
                        thread_data['forum_id'],
                        thread_data['creator_id'],
                        thread_data.get('reply_count', 0),
                        thread_data.get('views', 0)
                    )
                )
                thread_id = cursor.lastrowid
                
                # Update forum thread count
                conn.execute(
                    "UPDATE forums SET thread_count = thread_count + 1 WHERE id = ?",
                    (thread_data['forum_id'],)
                )
                
                # Update user stats
                conn.execute(
                    "UPDATE users SET threads_created = threads_created + 1 WHERE telegram_id = ?",
                    (thread_data['creator_id'],)
                )
                
                return thread_id
        except Exception as e:
            logging.error(f"Error creating thread: {e}")
            return 0

    # ==================== REPLY MANAGEMENT ====================
    def get_replies(self, thread_id: int) -> List[Dict[str, Any]]:
        """Get thread replies"""
        try:
            with self.get_connection() as conn:
                replies = conn.execute(
                    "SELECT r.*, u.username FROM replies r JOIN users u ON r.user_id = u.telegram_id WHERE r.thread_id = ? ORDER BY r.created_at ASC",
                    (thread_id,)
                ).fetchall()
                return [dict(reply) for reply in replies]
        except Exception as e:
            logging.error(f"Error getting replies: {e}")
            return []

    def create_reply(self, reply_data: Dict[str, Any]) -> int:
        """Create new reply"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO replies (content, thread_id, user_id) VALUES (?, ?, ?)",
                    (
                        reply_data['content'],
                        reply_data['thread_id'],
                        reply_data['user_id']
                    )
                )
                reply_id = cursor.lastrowid
                
                # Update thread reply count
                conn.execute(
                    "UPDATE threads SET reply_count = reply_count + 1, last_reply_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (reply_data['thread_id'],)
                )
                
                # Update forum reply count
                thread = conn.execute(
                    "SELECT forum_id FROM threads WHERE id = ?",
                    (reply_data['thread_id'],)
                ).fetchone()
                if thread:
                    conn.execute(
                        "UPDATE forums SET reply_count = reply_count + 1 WHERE id = ?",
                        (thread[0],)
                    )
                
                # Update user stats
                conn.execute(
                    "UPDATE users SET replies_posted = replies_posted + 1 WHERE telegram_id = ?",
                    (reply_data['user_id'],)
                )
                
                return reply_id
        except Exception as e:
            logging.error(f"Error creating reply: {e}")
            return 0

    # ==================== SOCIAL MANAGEMENT ====================
    def follow_user(self, follower_id: int, followed_id: int) -> bool:
        """Follow a user"""
        try:
            with self.get_connection() as conn:
                # Check if already following
                existing = conn.execute(
                    "SELECT id FROM user_follows WHERE follower_id = ? AND followed_id = ?",
                    (follower_id, followed_id)
                ).fetchone()
                
                if existing or follower_id == followed_id:
                    return False
                
                # Create follow relationship
                conn.execute(
                    "INSERT INTO user_follows (follower_id, followed_id) VALUES (?, ?)",
                    (follower_id, followed_id)
                )
                
                # Update stats
                conn.execute(
                    "UPDATE user_stats SET following_count = following_count + 1 WHERE user_id = ?",
                    (follower_id,)
                )
                conn.execute(
                    "UPDATE user_stats SET follower_count = follower_count + 1 WHERE user_id = ?",
                    (followed_id,)
                )
                
                return True
        except Exception as e:
            logging.error(f"Error following user: {e}")
            return False

    def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        """Unfollow a user"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    "DELETE FROM user_follows WHERE follower_id = ? AND followed_id = ?",
                    (follower_id, followed_id)
                )
                
                if result.rowcount > 0:
                    # Update stats
                    conn.execute(
                        "UPDATE user_stats SET following_count = following_count - 1 WHERE user_id = ?",
                        (follower_id,)
                    )
                    conn.execute(
                        "UPDATE user_stats SET follower_count = follower_count - 1 WHERE user_id = ?",
                        (followed_id,)
                    )
                    return True
                return False
        except Exception as e:
            logging.error(f"Error unfollowing user: {e}")
            return False

    def get_user_followers(self, user_id: int) -> List[int]:
        """Get user followers"""
        try:
            with self.get_connection() as conn:
                followers = conn.execute(
                    "SELECT follower_id FROM user_follows WHERE followed_id = ?",
                    (user_id,)
                ).fetchall()
                return [row[0] for row in followers]
        except Exception as e:
            logging.error(f"Error getting user followers: {e}")
            return []

    def get_user_following(self, user_id: int) -> List[int]:
        """Get users followed by user"""
        try:
            with self.get_connection() as conn:
                following = conn.execute(
                    "SELECT followed_id FROM user_follows WHERE follower_id = ?",
                    (user_id,)
                ).fetchall()
                return [row[0] for row in following]
        except Exception as e:
            logging.error(f"Error getting user following: {e}")
            return []

    def follow_forum(self, user_id: int, forum_id: int) -> bool:
        """Follow a forum"""
        try:
            with self.get_connection() as conn:
                # Check if already following
                existing = conn.execute(
                    "SELECT id FROM forum_follows WHERE user_id = ? AND forum_id = ?",
                    (user_id, forum_id)
                ).fetchone()
                
                if existing:
                    return False
                
                conn.execute(
                    "INSERT INTO forum_follows (user_id, forum_id) VALUES (?, ?)",
                    (user_id, forum_id)
                )
                return True
        except Exception as e:
            logging.error(f"Error following forum: {e}")
            return False

    def unfollow_forum(self, user_id: int, forum_id: int) -> bool:
        """Unfollow a forum"""
        try:
            with self.get_connection() as conn:
                result = conn.execute(
                    "DELETE FROM forum_follows WHERE user_id = ? AND forum_id = ?",
                    (user_id, forum_id)
                )
                return result.rowcount > 0
        except Exception as e:
            logging.error(f"Error unfollowing forum: {e}")
            return False

    def get_user_forum_follows(self, user_id: int) -> List[int]:
        """Get forums followed by user"""
        try:
            with self.get_connection() as conn:
                follows = conn.execute(
                    "SELECT forum_id FROM forum_follows WHERE user_id = ?",
                    (user_id,)
                ).fetchall()
                return [row[0] for row in follows]
        except Exception as e:
            logging.error(f"Error getting user forum follows: {e}")
            return []

    # ==================== BADGE MANAGEMENT ====================
    def get_badges(self) -> List[Dict[str, Any]]:
        """Get all badges"""
        try:
            with self.get_connection() as conn:
                badges = conn.execute("SELECT * FROM badges").fetchall()
                return [dict(badge) for badge in badges]
        except Exception as e:
            logging.error(f"Error getting badges: {e}")
            return []

    def award_badge(self, user_id: int, badge_name: str):
        """Award badge to user"""
        try:
            with self.get_connection() as conn:
                # Check if already has badge
                existing = conn.execute(
                    "SELECT id FROM user_badges WHERE user_id = ? AND badge_name = ?",
                    (user_id, badge_name)
                ).fetchone()
                
                if not existing:
                    conn.execute(
                        "INSERT INTO user_badges (user_id, badge_name) VALUES (?, ?)",
                        (user_id, badge_name)
                    )
                    
                    # Update badge count
                    conn.execute(
                        "UPDATE user_stats SET badge_count = badge_count + 1 WHERE user_id = ?",
                        (user_id,)
                    )
        except Exception as e:
            logging.error(f"Error awarding badge: {e}")

    def get_user_badges(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user badges"""
        try:
            with self.get_connection() as conn:
                badges = conn.execute(
                    "SELECT * FROM user_badges WHERE user_id = ? ORDER BY awarded_at DESC",
                    (user_id,)
                ).fetchall()
                return [dict(badge) for badge in badges]
        except Exception as e:
            logging.error(f"Error getting user badges: {e}")
            return []

    # ==================== STATISTICS ====================
    def get_quick_stats(self) -> Dict[str, Any]:
        """Get quick community statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                queries = {
                    'total_users': "SELECT COUNT(*) FROM users",
                    'total_threads': "SELECT COUNT(*) FROM threads",
                    'total_replies': "SELECT COUNT(*) FROM replies",
                    'total_tournaments': "SELECT COUNT(*) FROM tournaments",
                    'active_tournaments': "SELECT COUNT(*) FROM tournaments WHERE status = 'active'"
                }
                
                for key, query in queries.items():
                    stats[key] = conn.execute(query).fetchone()[0]
                
                return stats
        except Exception as e:
            logging.error(f"Error getting quick stats: {e}")
            return {}

    def get_user_rankings(self, limit: int = 10, criteria: str = 'reputation') -> List[Dict[str, Any]]:
        """Get user rankings"""
        valid_criteria = ['reputation', 'level', 'threads_created', 'replies_posted']
        if criteria not in valid_criteria:
            criteria = 'reputation'
            
        try:
            with self.get_connection() as conn:
                rankings = conn.execute(
                    f"SELECT telegram_id, username, level, reputation, threads_created, replies_posted FROM users ORDER BY {criteria} DESC LIMIT ?",
                    (limit,)
                ).fetchall()
                return [dict(rank) for rank in rankings]
        except Exception as e:
            logging.error(f"Error getting user rankings: {e}")
            return []

    def get_all_users(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            with self.get_connection() as conn:
                users = conn.execute(
                    "SELECT telegram_id, username, level, reputation FROM users ORDER BY reputation DESC LIMIT ?",
                    (limit,)
                ).fetchall()
                return [dict(user) for user in users]
        except Exception as e:
            logging.error(f"Error getting all users: {e}")
            return []