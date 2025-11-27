import psycopg2
import json
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from pathlib import Path
import logging
import datetime
import math

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
        
        safe_params = {k: v for k, v in conn_params.items() if k != 'password'}
        logger.debug(f"DBHelper.connect: Attempting connection with {safe_params}")

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
        """Create the comprehensive schema tables."""
        # Drop old tables first if needed? 
        # User said "make these tables". We'll assume fresh start or IF NOT EXISTS. 
        # But to ensure schema changes take effect, we should ideally drop. 
        # However, "IF NOT EXISTS" is safer for data retention if user didn't ask to drop.
        # Given "I want these tables... to be made", I'll assume we can create them.
        # If they conflict with old 'submissions' table, we might have issues.
        # I will drop the old ones to ensure the new structure applies.
        
        commands = (
            "DROP TABLE IF EXISTS judging_results CASCADE",
            "DROP TABLE IF EXISTS comments CASCADE",
            "DROP TABLE IF EXISTS submissions CASCADE", # Replaced by ideas
            "DROP TABLE IF EXISTS users CASCADE",
            "DROP TABLE IF EXISTS rubrics CASCADE",
            "DROP TABLE IF EXISTS hackathons CASCADE",
            "DROP TABLE IF EXISTS ideas CASCADE",
            "DROP TABLE IF EXISTS extractions CASCADE",
            "DROP TABLE IF EXISTS classifications CASCADE",
            "DROP TABLE IF EXISTS evaluations CASCADE",
            "DROP TABLE IF EXISTS verifications CASCADE",
            "DROP TABLE IF EXISTS full_results CASCADE",

            """
            CREATE TABLE hackathons (
                hackathon_id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                description TEXT,
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                role VARCHAR(50) DEFAULT 'participant'
            )
            """,
            """
            CREATE TABLE rubrics (
                rubric_id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(hackathon_id) ON DELETE CASCADE,
                rubric_name VARCHAR(255),
                description TEXT
            )
            """,
            """
            CREATE TABLE ideas (
                db_idea_id SERIAL PRIMARY KEY,
                hackathon_id INTEGER REFERENCES hackathons(hackathon_id) ON DELETE CASCADE,
                external_idea_id VARCHAR(255),
                title TEXT,
                summary TEXT,
                challenge_opportunity TEXT,
                novelty_benefits_risks TEXT,
                responsible_ai TEXT,
                preferred_week VARCHAR(255),
                build_preference VARCHAR(255),
                build_approach VARCHAR(255),
                code_preference VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE extractions (
                extraction_id SERIAL PRIMARY KEY,
                db_idea_id INTEGER REFERENCES ideas(db_idea_id) ON DELETE CASCADE,
                extracted_content TEXT,
                content_type VARCHAR(50),
                file_paths TEXT
            )
            """,
            """
            CREATE TABLE classifications (
                classification_id SERIAL PRIMARY KEY,
                db_idea_id INTEGER REFERENCES ideas(db_idea_id) ON DELETE CASCADE,
                primary_theme VARCHAR(255),
                secondary_themes TEXT,
                theme_confidence DECIMAL(5,2),
                theme_rationale TEXT,
                primary_industry VARCHAR(255),
                secondary_industries TEXT,
                industry_confidence DECIMAL(5,2),
                industry_rationale TEXT,
                technologies TEXT,
                technologies_rationale TEXT
            )
            """,
            """
            CREATE TABLE evaluations (
                evaluation_id SERIAL PRIMARY KEY,
                db_idea_id INTEGER REFERENCES ideas(db_idea_id) ON DELETE CASCADE,
                rubric_name VARCHAR(255),
                score DECIMAL(5,2),
                reasoning TEXT
            )
            """,
            """
            CREATE TABLE verifications (
                verification_id SERIAL PRIMARY KEY,
                db_idea_id INTEGER REFERENCES ideas(db_idea_id) ON DELETE CASCADE,
                status VARCHAR(50),
                comments TEXT,
                flagged_issues JSONB
            )
            """,
            """
            CREATE TABLE full_results (
                result_id SERIAL PRIMARY KEY,
                db_idea_id INTEGER REFERENCES ideas(db_idea_id) ON DELETE CASCADE,
                external_idea_id VARCHAR(255),
                full_json_data JSONB,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        try:
            self.connect()
            if not self.conn: 
                logger.error("Connection failed, cannot create tables.")
                return

            cur = self.conn.cursor()
            logger.info("Recreating tables with new schema...")
            for command in commands:
                cur.execute(command)
            
            self.conn.commit()
            cur.close()
            logger.info("New tables created successfully.")
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
        logger.info(f"Starting setup_hackathon: Name='{hackathon_name}'")
        hackathon_id = None
        rubric_map = {}
        try:
            self.connect()
            if not self.conn:
                return None, None

            cur = self.conn.cursor()

            # 1. Insert hackathon
            cur.execute("INSERT INTO hackathons (name, description, start_date) VALUES (%s, %s, %s) RETURNING hackathon_id",
                        (hackathon_name, hackathon_description, datetime.datetime.now()))
            hackathon_id = cur.fetchone()[0]
            
            # 2. Create default user (legacy support if needed, though not strictly used in new schema unless added)
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

    def _clean_json_data(self, data):
        """Recursively replace NaN/Infinity with None."""
        if isinstance(data, dict):
            return {k: self._clean_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._clean_json_data(v) for v in data]
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return None
        return data

    def insert_single_idea(self, hackathon_id, idea_data, rubric_map):
        """
        Inserts a single idea result into the comprehensive schema.
        """
        if not hackathon_id:
            return

        try:
            self.connect()
            if not self.conn:
                return

            cur = self.conn.cursor()
            
            # Clean all data first
            cleaned_data = self._clean_json_data(idea_data)
            
            # 1. Insert into IDEAS table
            cur.execute(
                """
                INSERT INTO ideas (
                    hackathon_id, external_idea_id, title, summary, 
                    challenge_opportunity, novelty_benefits_risks, responsible_ai,
                    preferred_week, build_preference, build_approach, code_preference
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING db_idea_id
                """,
                (
                    hackathon_id,
                    cleaned_data.get('idea_id'),
                    cleaned_data.get('idea_title') or cleaned_data.get('idea_name'),
                    cleaned_data.get('brief_summary') or cleaned_data.get('description'),
                    cleaned_data.get('challenge_opportunity'),
                    cleaned_data.get('novelty_benefits_risks'),
                    cleaned_data.get('responsible_ai'),
                    cleaned_data.get('preferred_week'),
                    cleaned_data.get('build_preference'),
                    cleaned_data.get('build_approach'),
                    cleaned_data.get('code_preference')
                )
            )
            db_idea_id = cur.fetchone()[0]
            logger.info(f"Inserted idea {cleaned_data.get('idea_id')} with DB ID {db_idea_id}")

            # 2. Insert into EXTRACTIONS table
            # Combine additional file types into a string or json
            file_paths = json.dumps(cleaned_data.get('additional_file_types', []))
            llm_out = cleaned_data.get('llm_output', {})
            
            cur.execute(
                "INSERT INTO extractions (db_idea_id, extracted_content, content_type, file_paths) VALUES (%s, %s, %s, %s)",
                (
                    db_idea_id,
                    llm_out.get('extracted_files_content', '')[:100000], # Limit size if needed
                    llm_out.get('content_type'),
                    file_paths
                )
            )

            # 3. Insert into CLASSIFICATIONS table
            theme_data = llm_out.get('theme', {})
            industry_data = llm_out.get('industry', {})
            tech_data = llm_out.get('technologies', {})
            
            # Helper to get string from list or string
            def to_str(val):
                if isinstance(val, list): return ", ".join(map(str, val))
                return str(val) if val else None

            cur.execute(
                """
                INSERT INTO classifications (
                    db_idea_id, 
                    primary_theme, secondary_themes, theme_confidence, theme_rationale,
                    primary_industry, secondary_industries, industry_confidence, industry_rationale,
                    technologies, technologies_rationale
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    db_idea_id,
                    theme_data.get('primary_theme'),
                    to_str(theme_data.get('secondary_themes')),
                    theme_data.get('confidence'),
                    theme_data.get('rationale'),
                    industry_data.get('primary_industry') or industry_data.get('industry_name'), # Handle industry_name key
                    to_str(industry_data.get('secondary_industries')),
                    industry_data.get('confidence'),
                    industry_data.get('rationale'),
                    to_str(tech_data.get('technologies_extracted') or tech_data.get('technologies')), # Handle extracted vs raw
                    tech_data.get('rationale')
                )
            )

            # 4. Insert into EVALUATIONS table
            eval_data = llm_out.get('evaluation', {})
            # Handle nested criteria
            if 'criteria' in eval_data and isinstance(eval_data['criteria'], dict):
                eval_data.update(eval_data['criteria'])
            
            for r_name, r_val in eval_data.items():
                # Skip metadata keys
                if r_name.upper() in ['SCHEMA_VERSION', 'RUBRIC_WEIGHTS', 'WEIGHTED_TOTAL', 'INVESTMENT_RECOMMENDATION', 'KEY_STRENGTHS', 'KEY_CONCERNS', 'ASSUMPTIONS', 'FLAGS', 'CRITERIA', 'PROTOTYPE_BONUS_APPLIED']:
                    continue
                
                score = None
                reasoning = None
                if isinstance(r_val, dict):
                    score = r_val.get('score')
                    # Check for reasoning OR justification
                    reasoning = r_val.get('reasoning') or r_val.get('justification')
                else:
                    score = r_val # Assume it's just the score
                
                # Ensure score is float-compatible
                if score is not None:
                    # Handle boolean scores just in case
                    if isinstance(score, bool):
                         continue # Skip boolean flags that aren't in ignore list
                    try:
                        float(score)
                        cur.execute(
                            "INSERT INTO evaluations (db_idea_id, rubric_name, score, reasoning) VALUES (%s, %s, %s, %s)",
                            (db_idea_id, r_name, score, reasoning)
                        )
                    except ValueError:
                        logger.warning(f"Invalid score for rubric {r_name}: {score}")

            # 5. Insert into VERIFICATIONS table
            verif_data = idea_data.get('verification', {}) # Get from root idea_data, NOT llm_out
            cur.execute(
                "INSERT INTO verifications (db_idea_id, status, comments, flagged_issues) VALUES (%s, %s, %s, %s)",
                (
                    db_idea_id,
                    verif_data.get('verification_status') or verif_data.get('status'),
                    str(verif_data.get('warnings', '')) if verif_data.get('warnings') else verif_data.get('comments'),
                    json.dumps(verif_data) # Store full object for debugging/completeness
                )
            )

            # 6. Insert into FULL_RESULTS table
            cur.execute(
                "INSERT INTO full_results (db_idea_id, external_idea_id, full_json_data) VALUES (%s, %s, %s)",
                (db_idea_id, cleaned_data.get('idea_id'), json.dumps(cleaned_data))
            )

            self.conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error inserting idea: {error}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.close()

    def get_results_as_json(self, hackathon_id):
        """Fetch results from the comprehensive schema."""
        try:
            self.connect()
            if not self.conn: 
                return json.dumps({"error": "Connection failed"})

            cur = self.conn.cursor()
            # Simplified fetch from full_results for now
            cur.execute("SELECT full_json_data FROM full_results fr JOIN ideas i ON fr.db_idea_id = i.db_idea_id WHERE i.hackathon_id = %s", (hackathon_id,))
            
            results = []
            for row in cur.fetchall():
                results.append(row[0])

            cur.close()
            return json.dumps(results, indent=2)

        except Exception as error:
            return json.dumps({"error": str(error)})
        finally:
            self.close()