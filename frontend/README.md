# CVR GPT Frontend

Next.js frontend for the CVR GPT application.

## Development

```bash
npm run dev
```

## API Types

The frontend uses auto-generated TypeScript types from the backend OpenAPI schema.

### Regenerate API types

After making changes to the backend API:

1. **From static file** (after running `python server/scripts/export_openapi.py`):
   ```bash
   npm run gen:types
   ```

2. **From live server** (make sure backend is running on localhost:8000):
   ```bash
   npm run gen:types:live
   ```

The generated types will be available in `src/types/api.ts`.
