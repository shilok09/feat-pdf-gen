# Supabase Upload Guide

This guide explains how to set up and use the Supabase Storage uploader to automatically upload generated PDF offers to your Supabase storage bucket.

## 📋 Prerequisites

1. **Supabase Account**: Create a free account at [supabase.com](https://supabase.com)
2. **Supabase Project**: Create a new project or use an existing one
3. **Storage Bucket**: Create a storage bucket named `offers` (or use a custom name)

---

## 🔧 Setup Instructions

### Step 1: Get Your Supabase Credentials

1. Go to your [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Settings** → **API**
4. Copy the following:
   - **Project URL** (e.g., `https://xxxxxxxxxxxxx.supabase.co`)
   - **API Key** (use `service_role` key for server-side uploads)

### Step 2: Create Storage Bucket

1. In Supabase Dashboard, go to **Storage**
2. Click **New bucket**
3. Name it `offers`
4. Set as **Public** if you want files to be publicly accessible
5. Click **Create bucket**

### Step 3: Configure Credentials

**Option 1: Using Environment Variables (Recommended)**

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` file and add your credentials:
   ```env
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-service-role-key-here
   ```

**Option 2: Pass Credentials Directly**

You can also pass credentials when initializing the uploader:
```python
from supabaseUploader import SupabaseUploader

uploader = SupabaseUploader(
    supabase_url="https://your-project-id.supabase.co",
    supabase_key="your-service-role-key"
)
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Basic Upload Example

```python
from supabaseUploader import SupabaseUploader

# Initialize uploader
uploader = SupabaseUploader()

# Upload a PDF from finalPdf folder
result = uploader.upload_from_finalPdf_folder("MUTTI Technologies.pdf")

if result["success"]:
    print(f"✅ Uploaded successfully!")
    print(f"Public URL: {result['url']}")
else:
    print(f"❌ Upload failed: {result['error']}")
```

### Upload Custom File

```python
# Upload any PDF file
result = uploader.upload_pdf(
    file_path="/path/to/your/file.pdf",
    destination_path="offers/2024/january/offer_123.pdf"
)
```

### List Files in Bucket

```python
files = uploader.list_files()
for file in files:
    print(file['name'])
```

### Delete File

```python
success = uploader.delete_file("MUTTI Technologies.pdf")
```

---

## 🔗 Integration with Workflow

### Automatic Upload After PDF Generation

You can integrate the uploader into your workflow to automatically upload PDFs after generation:

```python
from workflow import WorkflowOrchestrator
from supabaseUploader import SupabaseUploader

# Generate PDF
orchestrator = WorkflowOrchestrator()
pdf_path = await orchestrator.run()

if pdf_path:
    # Upload to Supabase
    uploader = SupabaseUploader()
    pdf_filename = Path(pdf_path).name
    
    result = uploader.upload_from_finalPdf_folder(pdf_filename)
    
    if result["success"]:
        print(f"✅ PDF uploaded to: {result['url']}")
        # Store the URL in your database
        offer_url = result['url']
```

---

## 📊 Response Format

All upload operations return a dictionary with the following structure:

**Success Response:**
```python
{
    "success": True,
    "url": "https://xxxxx.supabase.co/storage/v1/object/public/offers/file.pdf",
    "path": "file.pdf",
    "bucket": "offers",
    "file_name": "file.pdf"
}
```

**Error Response:**
```python
{
    "success": False,
    "error": "Error message describing what went wrong"
}
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**: It's already in `.gitignore`
2. **Use service_role key**: For server-side operations (more secure)
3. **Set bucket policies**: Configure Row Level Security (RLS) in Supabase
4. **Validate files**: The uploader automatically validates PDF files before upload

---

## 🌐 Bucket URL Pattern

Your uploaded files will be accessible at:
```
https://[project-id].supabase.co/storage/v1/object/public/offers/[file-name].pdf
```

Example:
```
https://uhldhrwvpbhbfurebvao.supabase.co/storage/v1/object/public/offers/MUTTI Technologies.pdf
```

---

## 🧪 Testing the Uploader

Run the test script:

```bash
python supabaseUploader.py
```

This will:
1. Initialize the Supabase client
2. Attempt to upload a test PDF
3. List all files in the bucket
4. Show the public URL

---

## ❓ Troubleshooting

### Error: "Supabase credentials not found"
- Make sure you've created the `.env` file
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
- Restart your application after adding environment variables

### Error: "Bucket not found"
- Make sure you've created the `offers` bucket in Supabase Dashboard
- Check bucket name spelling (case-sensitive)
- Verify bucket is set to public if you want public URLs

### Error: "Permission denied"
- Make sure you're using the `service_role` key, not the `anon` key
- Check bucket policies and Row Level Security settings

### Upload succeeds but URL returns 404
- Verify bucket is set to **public** in Supabase Dashboard
- Check the file path in the bucket

---

## 📚 Additional Resources

- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Supabase Python Client Docs](https://github.com/supabase/supabase-py)
- [Storage API Reference](https://supabase.com/docs/reference/python/storage)

---

## 🎯 Next Steps

After setting up the uploader, you can:
1. Integrate it into your FastAPI endpoint
2. Store the returned URLs in your database
3. Send the URLs to clients via email or API response
4. Set up automatic cleanup of old offers
5. Implement file versioning

---

For questions or issues, please contact the development team.

