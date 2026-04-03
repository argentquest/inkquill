# RunPod ComfyUI Flux Setup Guide

## 🚀 Quick Setup Steps

### 1. **Database Setup**
Run the SQL script to add RunPod model configurations:
```bash
# Connect to your PostgreSQL database and run:
psql -h your-host -d your-database -f add_runpod_model_config.sql
```

### 2. **Environment Variables**
Add these to your `.env` file:
```env
# RunPod ComfyUI Configuration
RUNPOD_API_KEY=your_runpod_api_key_here
RUNPOD_ENDPOINT_ID=your_comfyui_endpoint_id_here
RUNPOD_MODEL_TYPE=flux-dev
RUNPOD_CHECKPOINT_NAME=flux1-dev.safetensors

# Switch to RunPod as active provider
ACTIVE_IMAGE_PROVIDER=RUNPOD
```

### 3. **RunPod ComfyUI Endpoint Setup**
In your RunPod account:
1. Create a new **Serverless Endpoint**
2. Choose a **ComfyUI** template with Flux support
3. Copy the **Endpoint ID** to your `.env` file
4. Get your **API Key** from RunPod dashboard

#### **Recommended ComfyUI Templates:**
- `comfyui/comfyui:latest-flux`
- `runpod/comfyui-flux`
- `comfyanonymous/comfyui-flux-dev`

### 4. **Test the Implementation**
1. Restart your application
2. Try generating an image through the UI
3. Check the admin jobs page to verify costs

## 💰 Cost Comparison

| Model | Cost per Image | Quality | Speed |
|-------|---------------|---------|-------|
| **Flux Dev (RunPod)** | **1 coin** | Excellent | Fast |
| Flux Pro (RunPod) | 5 coins | Premium | Fast |
| SD XL (RunPod) | 0.5 coins | Good | Very Fast |
| DALL-E 3 (Current) | 400 coins | Premium | Medium |

## 🛠️ ComfyUI Endpoint Setup Details

### **Creating ComfyUI Flux Endpoint:**

1. **Go to RunPod → Serverless → New Endpoint**
2. **Search for ComfyUI templates:**
   - Look for "comfyui", "flux", or "comfy"
   - Choose templates with Flux support
3. **Recommended Settings:**
   ```
   Name: comfyui-flux-endpoint
   Template: ComfyUI with Flux
   Min Workers: 0
   Max Workers: 3
   Idle Timeout: 5 seconds
   GPU: RTX 4090 or A100
   Container Disk: 50GB (for Flux models)
   ```

### **ComfyUI Workflow Format:**
The provider sends this workflow structure:
```json
{
  "input": {
    "workflow": {
      "3": {"class_type": "KSampler", ...},
      "4": {"class_type": "CheckpointLoaderSimple", ...},
      "5": {"class_type": "EmptyLatentImage", ...}
    }
  }
}
```

### **Checkpoint Names to Try:**
- `flux1-dev.safetensors`
- `flux1-schnell.safetensors`
- `flux-dev-fp8.safetensors`
- `sd_xl_base_1.0.safetensors`

## 🔧 Troubleshooting

### Common Issues:
1. **Endpoint not responding**: Check if endpoint is active in RunPod dashboard
2. **Authentication failed**: Verify API key and endpoint ID
3. **Job timeout**: Increase timeout in RunPod provider (default 120s)

### Logs to Check:
```bash
# Check application logs for RunPod-specific errors
grep -i "runpod" logs/app_backend.log
```

## 📊 Monitoring

The RunPod integration includes:
- ✅ Cost tracking per image
- ✅ Job status monitoring  
- ✅ Error logging and handling
- ✅ Automatic retry on cold starts
- ✅ Admin dashboard integration

## 🎯 Next Steps

1. **Test thoroughly** with different prompts and sizes
2. **Monitor costs** in the admin billing dashboard
3. **Enable Flux Pro** for premium users if needed
4. **Scale endpoint** based on usage patterns

Your RunPod integration is now ready! 🎉