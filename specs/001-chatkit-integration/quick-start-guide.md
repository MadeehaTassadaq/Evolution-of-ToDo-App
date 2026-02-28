# Quick Start Guide: ChatKit Integration

## Prerequisites

1. Three terminal windows
2. Valid OpenAI API key
3. Neon PostgreSQL database credentials

## Step 1: Start Phase II Backend (Task CRUD)

```bash
# Terminal 1
cd phase_2_web_App/backend
python app.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Start Phase III Backend (ChatKit + AI)

```bash
# Terminal 2
cd phase_3_chatbot/backend
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860
```

## Step 3: Start Frontend

```bash
# Terminal 3
cd phase_2_web_App/frontend
npm run dev
```

Expected output:
```
▲ Next.js 16.x.x
- Local:        http://localhost:3000
- Network:      http://192.168.x.x:3000
```

## Step 4: Test the Integration

1. Open browser to `http://localhost:3000`
2. Login or register an account
3. ChatKit widget should appear in bottom-right corner
4. Try these commands:

### Test Commands

**Add a task:**
```
Add a task to buy groceries
```

**List tasks:**
```
Show me all my tasks
```

**List pending tasks:**
```
What do I need to do?
```

**Complete a task:**
```
Mark the groceries task as complete
```

**Update a task:**
```
Change the groceries task to buy groceries and milk
```

**Delete a task:**
```
Delete the groceries task
```

## Verification Checklist

- [ ] Phase II backend running on port 8000
- [ ] Phase III backend running on port 7860
- [ ] Frontend running on port 3000 or 3001
- [ ] Can login to the app
- [ ] ChatKit widget appears (bottom-right corner)
- [ ] Can send messages to the AI
- [ ] AI can add tasks
- [ ] AI can list tasks
- [ ] AI can complete tasks
- [ ] AI can delete tasks

## Troubleshooting Commands

### Check Phase II backend health:
```bash
curl http://localhost:8000/health
```

### Check Phase III backend health:
```bash
curl http://localhost:7860/health
```

### Check database connection:
```bash
cd phase_3_chatbot/backend
python -c "from database.session import engine; print('DB OK' if engine else 'DB FAIL')"
```

### View backend logs:
Both backends output logs to console, check for error messages.

### Check browser console:
Press F12 in browser and look for:
- Network errors (failed requests)
- JavaScript errors
- Auth token issues

## Environment Variables Reference

### Phase III Backend (.env)
```bash
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=phase2-local-development-secret-key-change-in-production-min-32-chars-please
OPENAI_API_KEY=sk-proj-...
FRONTEND_ORIGIN=http://localhost:3001
ENVIRONMENT=development
PORT=7860
OPENAI_CHATKIT_DOMAIN_KEY=domain_pk_...
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:7860
NEXT_PUBLIC_AUTH_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain_pk_...
NEXT_PUBLIC_ENABLE_CHATBOT=true
NEXT_PUBLIC_CHATKIT_URL=http://localhost:7860
```

## Common Issues

**Widget doesn't appear:**
- Check you're logged in
- Check `NEXT_PUBLIC_ENABLE_CHATBOT=true`
- Check browser console for errors

**"Connection refused":**
- Make sure Phase III backend is running
- Check it's on port 7860
- Check `NEXT_PUBLIC_CHATKIT_URL=http://localhost:7860`

**"401 Unauthorized":**
- Check BETTER_AUTH_SECRET matches in both backends
- Check you're logged in
- Check token in localStorage (F12 → Application → Local Storage)

**AI not responding:**
- Check OPENAI_API_KEY is valid
- Check you have API credits
- Check Phase III backend logs for OpenAI errors

**Tools not working:**
- Check database connection
- Check user_id is valid UUID
- Check Phase III backend logs for errors
