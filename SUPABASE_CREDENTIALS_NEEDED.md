# 🔑 Supabase Credentials Required

To enable PDF uploads to Supabase Storage, please provide the following credentials:

---

## Required Credentials

### 1. **SUPABASE_URL**
- **What is it?** Your Supabase project URL
- **Where to find it?** 
  - Go to [Supabase Dashboard](https://app.supabase.com)
  - Select your project
  - Navigate to **Settings** → **API**
  - Copy the **Project URL**
- **Format:** `https://xxxxxxxxxxxxx.supabase.co`
- **Example:** `https://uhldhrwvpbhbfurebvao.supabase.co`

### 2. **SUPABASE_KEY** 
- **What is it?** Your Supabase API Key
- **Where to find it?** 
  - Same location as above: **Settings** → **API**
  - Copy the **service_role** key (recommended for server-side)
  - ⚠️ **Do NOT use the `anon` public key** for uploads
- **Format:** Long alphanumeric string
- **Example:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 3. **Storage Bucket** (Already configured)
- **Bucket Name:** `offers`
- **Required Action:** Create this bucket in your Supabase Dashboard
  1. Go to **Storage** section
  2. Click **New bucket**
  3. Name it `offers`
  4. Set visibility to **Public**
  5. Click **Create bucket**

---

## How to Provide Credentials

### Option 1: Environment Variables (Recommended)

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here
```

### Option 2: Direct Configuration

Add to your configuration file or pass directly to the uploader.

---

## Bucket URL Pattern

Once configured, your uploaded PDFs will be accessible at:

```
https://[project-id].supabase.co/storage/v1/object/public/offers/[filename].pdf
```

**Your bucket URL pattern:**
```
https://uhldhrwvpbhbfurebvao.supabase.co/storage/v1/object/public/offers/{{ fileName }}
```

This matches the URL you provided! ✅

---

## Security Notes

- ✅ Keep your `service_role` key **SECRET**
- ✅ Never commit it to version control
- ✅ `.env` file is already in `.gitignore`
- ✅ Use environment variables in production

---

## Quick Start Checklist

- [ ] Get Supabase URL from dashboard
- [ ] Get service_role key from dashboard
- [ ] Create `offers` bucket in Supabase Storage
- [ ] Set bucket to public visibility
- [ ] Create `.env` file with credentials
- [ ] Run `pip install -r requirements.txt`
- [ ] Test upload with `python supabaseUploader.py`

---

**Ready to proceed?** Once you provide the credentials, the uploader will be fully functional! 🚀

