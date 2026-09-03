export async function onRequestPost(context) {
  try {
    const formData = await context.request.formData();
    const file = formData.get('file');
    const filename = formData.get('filename') || 'export.csv';

    if (!file) {
      return new Response(JSON.stringify({ error: 'No file provided' }), { 
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (!context.env.R2_STORAGE) {
      return new Response(JSON.stringify({ error: 'R2_STORAGE is not bound in Cloudflare settings' }), { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Generate a timestamped filename to prevent overwriting
    // Add 9 hours for KST (Korea Standard Time)
    const now = new Date();
    const kst = new Date(now.getTime() + (9 * 60 * 60 * 1000));
    const timestamp = kst.toISOString().replace(/[:.]/g, '-').replace('Z', '');
    
    const objectKey = `${timestamp}_${filename}`;

    // Upload to R2 bound as R2_STORAGE
    await context.env.R2_STORAGE.put(objectKey, file);

    return new Response(JSON.stringify({ 
      success: true, 
      message: 'File uploaded successfully to R2',
      key: objectKey 
    }), { 
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
