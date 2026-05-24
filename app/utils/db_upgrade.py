from sqlalchemy import text

def upgrade_database(app):
    """Automatically run idempotent DB upgrades to ensure gamification tables/columns exist."""
    from app.extensions import db
    
    with app.app_context():
        # Get the database dialect/engine name
        engine_name = db.engine.name
        app.logger.info(f"[DB-UPGRADE] Upgrading database with engine: {engine_name}")
        
        # 1. Idempotently add gamification columns to 'users' table
        user_columns = {
            "streak_count": "INTEGER DEFAULT 0",
            "last_sprint_date": "DATE",
            "xp": "INTEGER DEFAULT 0",
            "level": "INTEGER DEFAULT 1"
        }
        
        for column_name, column_def in user_columns.items():
            try:
                db.session.execute(text(f"SELECT {column_name} FROM users LIMIT 1"))
            except Exception:
                db.session.rollback()
                app.logger.info(f"[DB-UPGRADE] Adding column 'users.{column_name}'...")
                try:
                    db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"))
                    db.session.commit()
                    app.logger.info(f"[DB-UPGRADE] Column 'users.{column_name}' added successfully!")
                except Exception as e:
                    db.session.rollback()
                    app.logger.warning(f"[DB-UPGRADE] Warning: Could not add column 'users.{column_name}': {e}")
            else:
                app.logger.debug(f"[DB-UPGRADE] Column 'users.{column_name}' already exists.")

        # 2. Idempotently create 'user_sprint_submissions' table
        try:
            db.session.execute(text("SELECT id FROM user_sprint_submissions LIMIT 1"))
        except Exception:
            db.session.rollback()
            app.logger.info("[DB-UPGRADE] Table 'user_sprint_submissions' does not exist. Creating it...")
            
            # Determine appropriate types (JSONB for PostgreSQL, TEXT/JSON for others)
            json_type = "JSONB" if engine_name == "postgresql" else "TEXT"
            uuid_type = "UUID" if engine_name == "postgresql" else "VARCHAR(36)"
            date_type = "DATE"
            bool_type = "BOOLEAN"
            
            create_table_sql = f"""
            CREATE TABLE user_sprint_submissions (
                id {uuid_type} PRIMARY KEY,
                user_id {uuid_type} NOT NULL,
                sprint_date {date_type} NOT NULL,
                challenge_title VARCHAR(255) NOT NULL,
                challenge_type VARCHAR(50) NOT NULL,
                challenge_data {json_type} NOT NULL,
                user_answer TEXT,
                is_correct {bool_type} DEFAULT FALSE,
                ai_feedback TEXT,
                xp_earned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
            try:
                db.session.execute(text(create_table_sql))
                # Add unique index on (user_id, sprint_date) to ensure 1 submission per day
                db.session.execute(text("CREATE UNIQUE INDEX idx_user_sprint_date ON user_sprint_submissions (user_id, sprint_date)"))
                db.session.commit()
                app.logger.info("[DB-UPGRADE] Table 'user_sprint_submissions' created successfully!")
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"[DB-UPGRADE] Error creating 'user_sprint_submissions' table: {e}")
        else:
            app.logger.debug("[DB-UPGRADE] Table 'user_sprint_submissions' already exists.")
            
        # 3. Idempotently add portfolio columns to 'profiles' table
        profile_columns = {
            "portfolio_theme": "VARCHAR(50) DEFAULT 'zinc_indigo'",
            "portfolio_projects": "JSONB" if engine_name == "postgresql" else "TEXT",
            "portfolio_socials": "JSONB" if engine_name == "postgresql" else "TEXT"
        }
        
        for column_name, column_def in profile_columns.items():
            try:
                db.session.execute(text(f"SELECT {column_name} FROM profiles LIMIT 1"))
            except Exception:
                db.session.rollback()
                app.logger.info(f"[DB-UPGRADE] Adding column 'profiles.{column_name}'...")
                try:
                    db.session.execute(text(f"ALTER TABLE profiles ADD COLUMN {column_name} {column_def}"))
                    db.session.commit()
                    app.logger.info(f"[DB-UPGRADE] Column 'profiles.{column_name}' added successfully!")
                except Exception as e:
                    db.session.rollback()
                    app.logger.warning(f"[DB-UPGRADE] Warning: Could not add column 'profiles.{column_name}': {e}")
            else:
                app.logger.debug(f"[DB-UPGRADE] Column 'profiles.{column_name}' already exists.")
            
        app.logger.info("[DB-UPGRADE] Database upgrade checks completed.")
