#!/usr/bin/env python3
"""
Check database data format and distribution
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql+psycopg2", "postgresql")

def check_database():
    print("🔍 Checking Database Data\n")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check total records
        cursor.execute("SELECT COUNT(*) FROM resumes")
        total = cursor.fetchone()[0]
        print(f"📊 Total records: {total}")
        
        # Check confirmed records
        cursor.execute("SELECT COUNT(*) FROM resumes WHERE confirmed_role IS NOT NULL")
        confirmed = cursor.fetchone()[0]
        print(f"📈 Confirmed records: {confirmed}")
        
        # Check role distribution
        cursor.execute("""
            SELECT confirmed_role, COUNT(*) 
            FROM resumes 
            WHERE confirmed_role IS NOT NULL 
            GROUP BY confirmed_role 
            ORDER BY COUNT(*) DESC
        """)
        role_counts = cursor.fetchall()
        
        print(f"\n📊 Role distribution:")
        for role, count in role_counts:
            print(f"   {role}: {count}")
        
        # Check skills format
        cursor.execute("""
            SELECT extracted_skills, confirmed_role 
            FROM resumes 
            WHERE confirmed_role IS NOT NULL 
            LIMIT 5
        """)
        sample_data = cursor.fetchall()
        
        print(f"\n📝 Sample skills format:")
        for i, (skills, role) in enumerate(sample_data, 1):
            print(f"   Record {i} ({role}): {skills} (type: {type(skills)})")
        
        # Check if UI/UX Designer exists in data
        cursor.execute("""
            SELECT COUNT(*) 
            FROM resumes 
            WHERE confirmed_role = 'UI/UX Designer'
        """)
        uiux_count = cursor.fetchone()[0]
        print(f"\n🎨 UI/UX Designer records: {uiux_count}")
        
        # Check skills for UI/UX Designer records
        if uiux_count > 0:
            cursor.execute("""
                SELECT extracted_skills 
                FROM resumes 
                WHERE confirmed_role = 'UI/UX Designer' 
                LIMIT 3
            """)
            uiux_skills = cursor.fetchall()
            print(f"   Sample UI/UX Designer skills:")
            for i, (skills,) in enumerate(uiux_skills, 1):
                print(f"      {i}: {skills}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    check_database() 