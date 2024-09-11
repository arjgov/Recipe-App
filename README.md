# Recipe App

## Live Version
You can access the live version of the app at [https://recipe-app-xtxq.onrender.com](https://recipe-app-xtxq.onrender.com).

## Environment Configuration
Before running the application, ensure you have a `.env` file in the root directory. This file should contain the following variables:

```
SECRET_KEY="your_secret_key"
DB_NAME=your_database_name
DB_USERNAME=your_database_username
DB_PASSWORD=your_database_password
DB_HOSTNAME=your_database_hostname
DB_PORT=your_database_port

EMAIL_USER="your_email"
EMAIL_PASSWORD="your_email_password"

```

## Docker Setup
To compose and start the Docker container, run the following command in the root directory of the project:

```bash
docker compose up --build
```
Once the containers are up and running, you can access the app at [http://localhost:8000](http://localhost:8000).
There should be containers running for celery worker and celery beat as well, you can view that by running `docker ps`

## Error Handling

> **Note:** If you encounter any errors, you may need to run the following command manually to apply migrations:
>
> ```bash
> python manage.py migrate
> ```


## Alternative Running the Application locally
To run the application locally, use the following command:

```bash
python manage.py runserver
```

## Celery Worker and Beat
The application uses Celery for background tasks. The `celery beat` scheduler runs tasks at specified intervals. By default, the `send-daily-like-notifications` task is scheduled to run once a day.


> **Note:** 
> If you want to test the task more frequently, you can change the `CELERY_BEAT_SCHEDULE` in `config/settings/base.py` to run  every minute:
> You can modify the `CELERY_BEAT_SCHEDULE` as follows:
>
> ```python
> CELERY_BEAT_SCHEDULE = {
>     'send-daily-like-notifications': {
>         'task': 'recipe.tasks.send_daily_like_notifications',
>         'schedule': crontab(minute='*'),  # This will run the task every minute
>     },
> }
> ```
>
> After making this change, you will need to take down the Docker containers and redeploy them:
>
> ```bash
> docker compose down
> docker compos


## Running Tests and Coverage

To run the tests and check the coverage, you can use the following command:

```bash
docker-compose run test
```
or

```bash
pytest --cov=. --cov-report=html:htmlcov
```

After running the tests, the coverage report will be generated in the `htmlcov` directory. You can view the report by opening the `index.html` file in your web browser:


## Logging

The application logs are stored in the `logs` directory at the root of the project. The log files will be named according to the following pattern:

For example, a log file might be named `celery_worker.log.20240911-200253`, indicating that the log was created on September 11, 2024, at 20:02:53.

### Log File Location
- **Log Directory**: `logs/`
- **Log File Naming**: Each log file will have a timestamp appended to the filename, allowing you to keep track of logs over time.

## Conclusion