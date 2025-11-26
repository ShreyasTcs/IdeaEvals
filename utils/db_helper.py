import psycopg2
import json
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from pathlib import Path
import logging
import datetime

# Add project root to sys.path to allow importing config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.config import DB_CONFIG

logger = logging.getLogger(__name__)

class DBHelper:
    def __init__(self):
        self.conn = None

    def connect(self, db_name=None):
        """Connect to the PostgreSQL database server."""
        if db_name is None:
            db_name = DB_CONFIG.get('database', 'postgres')

        conn_params = DB_CONFIG.copy()
        conn_params['database'] = db_name
        
        try:
            self.conn = psycopg2.connect(**conn_params)
            self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_DEFAULT)
        except psycopg2.OperationalError as e:
            if f'database "{db_name}" does not exist' in str(e):
                logger.warning(f"Database '{db_name}' does not exist. Creating it...")
                self._create_database(db_name)
                try:
                    self.conn = psycopg2.connect(**conn_params)
                    self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_DEFAULT)
                except Exception as retry_error:
                    logger.error(f"Error connecting after DB creation: {retry_error}")
                    self.conn = None
            else:
                logger.error(f"Error connecting to the database: {e}")
                self.conn = None
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error connecting to the database: {error}")
            self.conn = None

    def _create_database(self, db_name):
        """Create the database if it does not exist."""
        conn_params = DB_CONFIG.copy()
        conn_params['database'] = 'postgres'
        
        conn = None
        try:
            conn = psycopg2.connect(**conn_params)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
            cur.close()
            logger.info(f"Database '{db_name}' created successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error creating database: {error}")
            raise error
        finally:
            if conn is not None:
                conn.close()

    def close(self):
        """Close the connection to the database."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def create_tables(self):
        """Create tables in the PostgreSQL database based on the comprehensive schema."""
        commands = (
            """
            CREATE TABLE IF NOT EXISTS hackathons (
                hackathon_id SERIAL PRIMARY KEY,
                hackathon_name VARCHAR(255) NOT NULL,
                description TEXT,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE,
                role VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS rubrics (
                rubric_id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(hackathon_id) ON DELETE CASCADE,
                rubric_name VARCHAR(255) NOT NULL,
                description TEXT,
                weightage DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(hackathon_id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                idea_name VARCHAR(255) NOT NULL,
                idea_description TEXT,
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                raw_data JSONB
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS judging_results (
                result_id SERIAL PRIMARY KEY,
                submission_id INTEGER REFERENCES submissions(submission_id) ON DELETE CASCADE,
                rubric_id INTEGER REFERENCES rubrics(rubric_id) ON DELETE CASCADE,
                judge_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                score INTEGER,
                reasoning TEXT,
                llm_output JSONB,
                judged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS comments (
                comment_id SERIAL PRIMARY KEY,
                submission_id INTEGER REFERENCES submissions(submission_id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
                comment_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        try:
            self.connect()
            if not self.conn: 
                logger.error("Connection failed, cannot create tables.")
                return

            cur = self.conn.cursor()
            logger.info("Creating/Verifying tables...")
            for command in commands:
                cur.execute(command)
            
            self.conn.commit()
            cur.close()
            logger.info("Tables verified successfully.")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error creating tables: {error}")
            if self.conn:
                self.conn.rollback()
            raise error
        finally:
            self.close()

    def setup_hackathon(self, hackathon_name, hackathon_description, rubrics):
        """
        Sets up the hackathon and rubrics.
        """
        hackathon_id = None
        rubric_map = {}
        try:
            self.connect()
            if not self.conn:
                logger.error("Connection failed, cannot setup hackathon.")
                return None, None

            cur = self.conn.cursor()

            # 1. Insert hackathon
            cur.execute("INSERT INTO hackathons (hackathon_name, description, start_date) VALUES (%s, %s, %s) RETURNING hackathon_id",
                        (hackathon_name, hackathon_description, datetime.datetime.now()))
            hackathon_id = cur.fetchone()[0]
            logger.info(f"Hackathon setup: ID {hackathon_id}")

            # 2. Create default user
            cur.execute("INSERT INTO users (username, role) VALUES (%s, %s) ON CONFLICT (username) DO NOTHING",
                        ('default_participant', 'participant'))
            
            # 3. Insert rubrics
            if isinstance(rubrics, dict):
                for rubric_name, details in rubrics.items():
                    desc = details.get('description', '') if isinstance(details, dict) else str(details)
                    cur.execute("INSERT INTO rubrics (hackathon_id, rubric_name, description) VALUES (%s, %s, %s) RETURNING rubric_id",
                                (hackathon_id, rubric_name, desc))
                    rubric_id = cur.fetchone()[0]
                    rubric_map[rubric_name] = rubric_id
            elif isinstance(rubrics, list):
                for item in rubrics:
                    rubric_name = None
                    rubric_desc = ''
                    
                    if isinstance(item, dict):
                        # Robust extraction for name
                        for key in ['rubric_name', 'name', 'criteria', 'title']:
                            if key in item:
                                rubric_name = item[key]
                                break
                        rubric_desc = item.get('description', '')
                    else:
                        rubric_name = str(item)

                    if rubric_name:
                        cur.execute("INSERT INTO rubrics (hackathon_id, rubric_name, description) VALUES (%s, %s, %s) RETURNING rubric_id",
                                    (hackathon_id, rubric_name, rubric_desc))
                        rubric_id = cur.fetchone()[0]
                        rubric_map[rubric_name] = rubric_id
                    else:
                        logger.warning(f"Could not extract rubric name from: {item}")

            self.conn.commit()
            cur.close()
            return hackathon_id, rubric_map

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error setting up hackathon: {error}")
            if self.conn:
                self.conn.rollback()
            return None, None
        finally:
            self.close()

    def insert_single_idea(self, hackathon_id, idea_data, rubric_map):
        """
        Inserts a single idea result.
        """
        if not hackathon_id:
            return

        try:
            self.connect()
            if not self.conn:
                return

            cur = self.conn.cursor()

            # Get user
            cur.execute("SELECT user_id FROM users WHERE username = %s", ('default_participant',))
            res = cur.fetchone()
            user_id = res[0] if res else None
            
            # Prepare data
            idea_name = idea_data.get('idea_title') or idea_data.get('idea_name', 'N/A')
            idea_desc = idea_data.get('brief_summary') or idea_data.get('description', '')

            # Insert Submission
            cur.execute(
                "INSERT INTO submissions (hackathon_id, user_id, idea_name, idea_description, raw_data) VALUES (%s, %s, %s, %s, %s) RETURNING submission_id",
                (hackathon_id, user_id, idea_name, idea_desc, json.dumps(idea_data))
            )
            submission_id = cur.fetchone()[0]

            # Insert Judging Results
            evaluation_data = idea_data.get('llm_output', {}).get('evaluation', {})
            if evaluation_data:
                for rubric_name, details in evaluation_data.items():
                    if rubric_name in rubric_map:
                        rubric_id = rubric_map[rubric_name]
                        cur.execute(
                            "INSERT INTO judging_results (submission_id, rubric_id, score, reasoning, llm_output) VALUES (%s, %s, %s, %s, %s)",
                            (submission_id, rubric_id, details.get('score'), details.get('reasoning'), json.dumps(idea_data.get('llm_output')))
                        )
                    else:
                        logger.warning(f"Rubric '{rubric_name}' in result but not in map (available: {list(rubric_map.keys())})")
            
            self.conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error inserting idea: {error}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.close()

    def get_results_as_json(self, hackathon_id):
        """Fetch results as JSON."""
        try:
            self.connect()
            if not self.conn: 
                return json.dumps({"error": "Database connection failed"}, indent=2)

            cur = self.conn.cursor()
            query = """
            SELECT s.idea_name, s.idea_description, r.rubric_name, jr.score, jr.reasoning
            FROM submissions s
            JOIN judging_results jr ON s.submission_id = jr.submission_id
            JOIN rubrics r ON jr.rubric_id = r.rubric_id
            WHERE s.hackathon_id = %s
            ORDER BY s.idea_name, r.rubric_name
            """
            cur.execute(query, (hackathon_id,))

            results = {}
            for row in cur.fetchall():
                idea_name, idea_description, rubric_name, score, reasoning = row
                if idea_name not in results:
                    results[idea_name] = {
                        'description': idea_description,
                        'evaluation': {}
                    }
                results[idea_name]['evaluation'][rubric_name] = {
                    'score': score,
                    'reasoning': reasoning
                }

            cur.close()
            return json.dumps(results, indent=2)

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error fetching results: {error}")
            return json.dumps({"error": str(error)}, indent=2)
        finally:
            self.close()
