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
