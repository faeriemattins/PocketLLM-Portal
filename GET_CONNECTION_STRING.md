# Get Your Supabase Connection String

## Steps:
1. In your Supabase project dashboard, click the **Settings** icon (⚙️) on the left sidebar
2. Click **Database** in the settings menu
3. Scroll down to the **Connection string** section
4. Click the **URI** tab (not the other tabs)
5. You'll see a string like:
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
6. **IMPORTANT**: Replace `[YOUR-PASSWORD]` with the database password you set when creating the project
7. Copy the complete connection string

## Example:
If your password is `mySecretPass123`, the final string should look like:
```
postgresql://postgres.xxxxx:mySecretPass123@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## Next Step:
Once you have the connection string, paste it here and I'll configure your app!
