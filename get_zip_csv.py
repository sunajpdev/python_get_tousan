from src.zip_code import getcsv
from dotenv import load_dotenv

load_dotenv('.env')

def main():
    getcsv.main()


if __name__ == "__main__":
    main()