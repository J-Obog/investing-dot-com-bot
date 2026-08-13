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

## Bot mention ingestor

The `BotMentionIngestor` polls every configured forum and persists posts that
mention the bot. Construct it with a `ForumApi` and a typed `BotConfig`:

```python
from config import BotConfig
from forum import ForumApi
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from bot_mention_ingestor import BotMentionIngestor

config = BotConfig.from_json("bot_config.json")
engine = create_engine(
    make_url(database_url).set(drivername="postgresql+psycopg")
)
with Session(engine) as db:
    ingestor = BotMentionIngestor(ForumApi(session_id), config, db)
    ingestor.run_iteration()
```

Run a fixed number of worker iterations from the admin CLI:

```powershell
uv run python admin.py worker 5
```

Use `--config path/to/config.json` to load a different bot configuration.
