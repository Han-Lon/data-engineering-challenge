## Changes to the project setup files
- I had to modify a few of the project files (the Makefile and docker-compose.yml) to get them to work on my Windows system.
  - If I had more time, I would've designed a way to have these files intelligently determine if they're running on a Windows or Unix machine, and then modify the commands as appropriate
  - If you're on a Unix system (Mac, Ubuntu, etc), you may have to revert back to the original files
    - You *shouldn't* have to, but if you run into issues, try that and see if it works

## How To Run
- Install all the prerequisites from the original README
- Make sure you've installed THIS project's required Python packages by running `pip install -r requirements.txt`
- Set the following environment variables:
  - (Windows)
    - `$env:ENDPOINT_URL="http://localhost:4566"`
    - `$env:QUEUE_URL="http://localhost:4566/000000000000/login-queue"`
    - `$env:DB_URL="postgresql://postgres:postgres@localhost:5432/postgres"`
  - (*nix)
    - `set ENDPOINT_URL=http://localhost:4566`
    - `set QUEUE_URL=http://localhost:4566/000000000000/login-queue`
    - `set DB_URL=postgresql://postgres:postgres@localhost:5432/postgres`
- Change directory into the solution/ folder
  - `cd solution`
- Execute the login_processor.py script
  - `python login_processor.py`
  - Make sure you're using the proper virtual environment-- the one where you installed all the packages in the second step

## Next Steps
- Port this functionality to an AWS service such as Lambda or ECS
  - What's nice about Lambda is you can trigger a Lambda function off of new messages in an SQS queue-- push trigger vs idle polling, and idle resources == money wasted :(
- Encrypt the hashed ip and device_id (if necessary) for further security
  - Can store the encryption key in AWS Secrets Manager for easy access by appropriate AWS services
  - This could be burdensome on the data analysts, so only implement if required
- Build more resiliency/error handling into the processor and database handler
  - There's already a decent amount, but there are some edge cases which could lead to annoying errors
- Make a nice wiki for how to set this up/get it working, as well as architecture diagrams :)
- Build out a CICD pipeline for deploying/updating the code in production
- Add size constraints to the UserLogin model within database_handler.py
  - Not a huge deal since the Postgres DB won't let us violate the size constraints it has defined, but I'd rather catch this in the processing phase rather than the DB commit phase