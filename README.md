# investing-dot-com-bot

## Database migrations

Set a PostgreSQL connection URL in `.env`:

```dotenv
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

Run migrations with the project-local dbmate executable:

```powershell
.\tools\dbmate.exe migrate
```

Other useful commands:

```powershell
.\tools\dbmate.exe status
.\tools\dbmate.exe rollback
.\tools\dbmate.exe new migration_name
```

## Mention worker

The `Worker` polls every configured forum and counts occurrences of the bot
mention. Construct it with a `ForumApi` and a typed `BotConfig`:

```python
from config import BotConfig
from forum import ForumApi
from worker import Worker

config = BotConfig.from_json("bot_config.json")
worker = Worker(ForumApi(session_id), config)

worker.run_iteration()
worker.run(iterations=5, interval=10)
worker.run()  # Run continuously, polling once per minute.
```
