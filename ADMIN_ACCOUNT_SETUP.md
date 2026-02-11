# TrustLink Admin Account Setup

## Create Admin Account for Railway Deployment

Since you're using a new PostgreSQL database on Railway, you need to create an admin account.

### Method 1: Using Railway CLI (Recommended)

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   railway link
   ```

4. **Run the admin creation script**:
   ```bash
   railway run python create_admin.py
   ```

5. **Follow the prompts**:
   ```
   Username: admin
   Email: your-email@example.com
   Password: YourSecurePassword123
   ```

6. **Done!** Your admin account is created.

---

### Method 2: Using Railway Database Terminal

1. **Go to Railway Dashboard**:
   - Visit: https://railway.app/dashboard
   - Click your TrustLink project

2. **Open PostgreSQL service**:
   - Click on the PostgreSQL database
   - Go to "Data" or "Query" tab

3. **Run this SQL**:
   ```sql
   -- Insert admin user (replace values)
   INSERT INTO users (username, email, password_hash, is_admin, is_active)
   VALUES (
     'admin',
     'your-email@example.com',
     encode(digest('YourPassword123', 'sha256'), 'hex'),
     TRUE,
     TRUE
   );
   ```

4. **Verify**:
   ```sql
   SELECT username, email, is_admin FROM users WHERE is_admin = TRUE;
   ```

---

### Method 3: Via Registration Page (Then Promote)

1. **Visit your Railway app**:
   ```
   https://your-app.railway.app/register
   ```

2. **Register a new account**:
   - Username: admin
   - Email: your-email@example.com
   - Password: YourPassword123

3. **Promote to admin via Railway Database**:
   - Go to Railway → PostgreSQL → Data/Query
   - Run:
   ```sql
   UPDATE users SET is_admin = TRUE WHERE username = 'admin';
   ```

4. **Logout and login again** to see admin features

---

### Method 4: Add Admin Creation Route (Temporary)

**⚠️ Security Warning: Remove this route after creating admin!**

Add this to `app.py` temporarily:

```python
@app.route('/create-first-admin', methods=['GET', 'POST'])
def create_first_admin():
    """Temporary route to create first admin - REMOVE AFTER USE"""
    
    # Check if any admin exists
    if db:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
            admin_count = cursor.fetchone()[0]
            
            if admin_count > 0:
                return "Admin already exists. Remove this route!", 403
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_id = db.create_user(username, email, password)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE users SET is_admin = TRUE WHERE id = %s',
                (user_id,)
            )
        
        return f"Admin '{username}' created! Now DELETE this route!"
    
    return '''
        <form method="post">
            Username: <input name="username"><br>
            Email: <input name="email"><br>
            Password: <input name="password" type="password"><br>
            <button>Create Admin</button>
        </form>
    '''
```

Then:
1. Deploy to Railway
2. Visit: `https://your-app.railway.app/create-first-admin`
3. Create admin account
4. **IMPORTANT**: Remove this route and redeploy!

---

## Recommended Admin Credentials

**Username**: `admin`  
**Email**: `your-email@example.com`  
**Password**: Use a strong password (min 12 characters)

### Generate Secure Password:
```bash
python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16)))"
```

---

## After Creating Admin

1. **Login at**: `https://your-app.railway.app/login`
2. **Access admin dashboard**: `https://your-app.railway.app/admin`
3. **Change password** (recommended):
   - Go to dashboard
   - Change to a memorable but secure password

---

## Default Login (For Local Testing)

If you're testing locally with SQLite:
- The old SQLite database may have old users
- Delete `trustlink.db` and restart to start fresh
- Or use the `create_admin.py` script locally

---

## Security Best Practices

✅ Use a unique, strong password  
✅ Use your real email for password recovery  
✅ Don't share admin credentials  
✅ Remove temporary admin creation routes  
✅ Change password after first login  

---

## Troubleshooting

**Issue: "User already exists"**
- Username or email is taken
- Use a different username/email

**Issue: "Database not available"**
- Check `DATABASE_URL` is set in Railway
- Verify PostgreSQL service is running

**Issue: Can't login**
- Verify user was created (check Railway DB)
- Check password is correct (case-sensitive)
- Ensure `is_admin = TRUE` in database

---

## Questions?

Which method would you like to use?
1. Railway CLI (easiest)
2. Database SQL (most direct)
3. Registration + Promotion (safest)
4. Temporary route (quick but requires cleanup)
