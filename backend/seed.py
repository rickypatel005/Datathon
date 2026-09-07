import os
import sys
import uuid
import shutil
import urllib.request
from sqlalchemy.orm import Session

# Add current dir to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.session import SessionLocal, Base, engine
from database.models import User, Dataset
from tools.analysis_tools import load_dataset, get_dataset_overview
from auth import hash_password
from config import settings

def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create user if not exists
        user = db.query(User).filter(User.username == "testuser").first()
        if not user:
            user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=hash_password("password123"),
                full_name="Test User"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Created test user: testuser / password123")
        else:
            print("Test user already exists.")

        # Ensure upload dir exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Download Titanic dataset
        url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}.csv")
        
        print("Downloading Titanic dataset...")
        urllib.request.urlretrieve(url, file_path)
        
        # Load and get overview
        print("Analyzing dataset metadata...")
        overview = get_dataset_overview.invoke({"file_path": file_path})
        
        # Create dataset entry
        dataset = Dataset(
            id=file_id,
            name="Titanic Passengers",
            original_filename="titanic.csv",
            file_path=file_path,
            file_type="csv",
            file_size=os.path.getsize(file_path),
            row_count=overview["shape"]["rows"],
            column_count=overview["shape"]["columns"],
            columns_metadata=overview["columns"],
            owner_id=user.id,
            status="ready"
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        print(f"Successfully seeded dataset '{dataset.name}' (ID: {dataset.id})")
        
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
