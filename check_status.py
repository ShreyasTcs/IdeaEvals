import psycopg2
from config.config import DB_CONFIG

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute('SELECT idea_id, extraction_status, classification_status FROM hackathon_ideas')

print('\n📊 IDEA STATUS:\n')
print(f"{'ID':<12} {'Extraction':<15} {'Classification'}")
print('-'*50)

for row in cur.fetchall():
    print(f"{row[0]:<12} {row[1]:<15} {row[2]}")

print()

# Check what the classification pipeline looks for
cur.execute("""
    SELECT COUNT(*) 
    FROM hackathon_ideas
    WHERE extraction_status = 'completed'
      AND (classification_status IS NULL OR classification_status = 'pending')
""")

count = cur.fetchone()[0]
print(f"Ideas needing classification: {count}")

cur.close()
conn.close()
