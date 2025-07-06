# Seed Data Generator for Resume Matcher

This script generates realistic seed data for the Resume Matcher application, creating 500+ resume records with diverse roles and skills.

## Features

- **15 Different Roles**: Full Stack Developer, Frontend Developer, Backend Developer, Data Scientist, Data Analyst, DevOps Engineer, Mobile Developer, UI/UX Designer, Product Manager, QA Engineer, Machine Learning Engineer, Cloud Engineer, Security Engineer, Database Administrator, Network Engineer
- **200+ Unique Skills**: Role-specific skill sets for each position
- **Realistic Data**: Generated resume text, email addresses, and match scores
- **Flexible Configuration**: Customizable number of records
- **Progress Tracking**: Real-time progress updates during seeding

## Prerequisites

1. Make sure your database is running and accessible
2. Set up your `.env` file with the `DATABASE_URL`
3. Install required dependencies:
   ```bash
   pip install sqlalchemy psycopg2-binary python-dotenv
   ```

## Usage

### Basic Usage (500 records)
```bash
cd backend
python seed_data.py
```

### Custom Number of Records
```bash
python seed_data.py 1000  # Generate 1000 records
python seed_data.py 250   # Generate 250 records
```

## What Gets Generated

Each record includes:
- **UUID**: Unique identifier
- **User Email**: Realistic email addresses
- **Raw Text**: Generated resume text based on role and skills
- **Extracted Skills**: 3-8 skills relevant to the role
- **Predicted Role**: The role assigned to the resume
- **Confirmed Role**: 70% chance of being confirmed (same as predicted)
- **Match Score**: Random score between 0.6 and 0.95
- **Created At**: Random date within the last 2 years

## Role Distribution

The script generates a balanced distribution across all 15 roles:
- Full Stack Developer
- Frontend Developer
- Backend Developer
- Data Scientist
- Data Analyst
- DevOps Engineer
- Mobile Developer
- UI/UX Designer
- Product Manager
- QA Engineer
- Machine Learning Engineer
- Cloud Engineer
- Security Engineer
- Database Administrator
- Network Engineer

## Sample Output

```
🌱 Resume Matcher Seed Data Generator
   Target records: 500
   Available roles: 15
   Total skills: 200+

✅ Database connected successfully
🚀 Starting to seed 500 records...
✅ Inserted 50 records...
✅ Inserted 100 records...
✅ Inserted 150 records...
...
🎉 Successfully seeded 500 records!

📊 Database Summary:
   Total records: 500
   Confirmed roles: 350
   Unconfirmed roles: 150

📈 Records by role:
   Full Stack Developer: 35
   Backend Developer: 33
   Data Scientist: 32
   Frontend Developer: 31
   ...
```

## Troubleshooting

### Database Connection Issues
- Verify your `DATABASE_URL` in the `.env` file
- Ensure your database is running and accessible
- Check firewall settings if using a remote database

### Permission Issues
- Make sure the script has write permissions to the database
- Verify your database user has INSERT privileges

### Memory Issues
- For large datasets (>1000 records), consider running in batches
- Monitor your database connection pool settings

## Customization

You can modify the script to:
- Add new roles and skills in the `SKILL_SETS` dictionary
- Adjust the resume text templates in `RESUME_TEMPLATES`
- Change the email generation logic
- Modify the match score range
- Adjust the confirmation rate (currently 70%)

## After Seeding

Once the seed data is generated, you can:
1. Retrain your ML model: `python train_model.py`
2. Test the prediction API with the new data
3. Analyze the distribution of roles and skills in your database

## Cleanup

To remove all seeded data (use with caution):
```sql
DELETE FROM resumes WHERE user_email LIKE '%.gmail.com' OR user_email LIKE '%.yahoo.com' OR user_email LIKE '%.hotmail.com';
``` 