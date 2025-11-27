# Migrating from Obsidian Local REST API Plugin

**Goal**: Replace the Obsidian Local REST API plugin with markdown-vault for more reliable, always-available API access.

## Why Migrate?

The Obsidian Local REST API plugin requires Obsidian to be running. **markdown-vault is a standalone service** that provides the same API without requiring Obsidian.

### Benefits of Migration

| Obsidian Plugin | markdown-vault |
|----------------|----------------|
| ✅ Works only when Obsidian is open | ✅ Always available (24/7) |
| ✅ Desktop only | ✅ Can run on servers, containers |
| ✅ One vault at a time | ✅ Multiple vaults supported |
| ✅ Tied to Obsidian performance | ✅ Dedicated, optimized service |
| ✅ Requires Obsidian installation | ✅ Works standalone |

**After migration**: Your existing API clients continue to work without changes!

## Migration Steps

### Step 1: Install markdown-vault

```bash
# Option 1: Using pip (when available)
pip install markdown-vault

# Option 2: Using Docker
docker pull markdown-vault:latest

# Option 3: From source
git clone https://github.com/yourusername/markdown-vault.git
cd markdown-vault
pip install -e .
```

### Step 2: Create Configuration

Create `config.yaml` pointing to your Obsidian vault:

```yaml
server:
  host: "127.0.0.1"
  port: 27123              # Same port as Obsidian plugin
  https: true

vault:
  path: "/Users/you/Documents/MyObsidianVault"  # Your vault path
  auto_create: false       # Vault already exists

security:
  api_key: null            # Will auto-generate or set your own
  cert_path: "./certs/server.crt"
  key_path: "./certs/server.key"
  auto_generate_cert: true

obsidian:
  enabled: true            # Read Obsidian configuration
  config_sync: true        # Import periodic notes settings
  respect_exclusions: true
```

### Step 3: Get Your Obsidian Plugin Settings (Optional)

If you want to use the same API key:

1. Open Obsidian
2. Go to Settings → Community Plugins → Local REST API
3. Copy your API key
4. Add it to your `config.yaml`:

```yaml
security:
  api_key: "your-copied-api-key-here"
```

**Note**: You don't have to use the same key - markdown-vault can generate a new one.

### Step 4: Disable Obsidian Plugin

**Important**: Stop the Obsidian plugin before starting markdown-vault (both use port 27123).

1. Open Obsidian
2. Go to Settings → Community Plugins
3. Toggle off "Local REST API"
4. (Optional) You can now close Obsidian - markdown-vault doesn't need it!

### Step 5: Start markdown-vault

```bash
# Start the service
markdown-vault start --config config.yaml

# Or using Docker
docker-compose up -d
```

The service will:
- Start on the same port (27123)
- Use HTTPS (self-signed cert or existing cert)
- Read your Obsidian vault structure
- Import periodic notes settings from `.obsidian/`
- Work exactly like the plugin

### Step 6: Test the API

```bash
# Test basic endpoint
curl -k https://localhost:27123/

# Should return:
{
  "ok": "OK",
  "service": "markdown-vault",
  "authenticated": false,
  "versions": {...}
}

# Test with authentication
curl -k -H "Authorization: Bearer YOUR_API_KEY" \
  https://localhost:27123/vault/
```

### Step 7: Update Your Client Applications (If Needed)

Most clients won't need changes, but you may need to:

1. **Update API Key**: If you generated a new key
   ```javascript
   const apiKey = "your-new-markdown-vault-key";
   ```

2. **Update Certificate** (if using self-signed cert):
   ```bash
   # Download the new cert
   curl -k https://localhost:27123/obsidian-local-rest-api.crt > cert.crt
   
   # Trust it in your application
   ```

3. **Test All Endpoints**: Ensure your application still works

## Configuration Sync

markdown-vault can automatically import settings from Obsidian:

### Periodic Notes

If you have the Periodic Notes plugin configured in Obsidian:

```json
// .obsidian/plugins/periodic-notes/data.json
{
  "daily": {
    "format": "YYYY-MM-DD",
    "folder": "Daily Notes",
    "template": "Templates/Daily.md"
  },
  "weekly": {
    "format": "YYYY-[W]WW",
    "folder": "Weekly Notes"
  }
}
```

markdown-vault will automatically read these settings when `obsidian.config_sync: true`.

### Templates

If you use templates, ensure they're in your vault and referenced correctly.

## Running Both (Advanced)

You can run both the plugin and markdown-vault, but they **cannot use the same port**.

**Option 1**: Change markdown-vault port:
```yaml
server:
  port: 27124  # Different port
```

**Option 2**: Change Obsidian plugin port (in Obsidian settings)

**Recommended**: Just use markdown-vault - it's more reliable and doesn't require Obsidian to run.

## Docker Deployment

For server deployment:

### docker-compose.yml
```yaml
version: '3.8'

services:
  markdown-vault:
    image: markdown-vault:latest
    ports:
      - "27123:27123"
    volumes:
      - /path/to/obsidian/vault:/vault
      - ./config:/config
      - ./certs:/certs
    environment:
      - MARKDOWN_VAULT_API_KEY=${API_KEY}
    restart: unless-stopped
```

### Run
```bash
docker-compose up -d
```

Now your vault is accessible 24/7 from anywhere (with proper network config).

## Systemd Service (Linux)

For always-on service on Linux:

### /etc/systemd/system/markdown-vault.service
```ini
[Unit]
Description=markdown-vault API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/markdown-vault
ExecStart=/usr/local/bin/markdown-vault start --config /etc/markdown-vault/config.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Enable and start
```bash
sudo systemctl enable markdown-vault
sudo systemctl start markdown-vault
sudo systemctl status markdown-vault
```

## Troubleshooting

### Port Already in Use

**Error**: `Address already in use: 27123`

**Solution**: Ensure Obsidian plugin is disabled:
```bash
# Check what's using the port
lsof -i :27123

# Kill the process if needed
kill -9 <PID>
```

### Certificate Issues

**Error**: `SSL certificate verify failed`

**Solution 1**: Use `-k` flag with curl (testing only):
```bash
curl -k https://localhost:27123/
```

**Solution 2**: Trust the certificate:
```bash
# Download cert
curl -k https://localhost:27123/obsidian-local-rest-api.crt > cert.crt

# Trust it (macOS)
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain cert.crt

# Trust it (Linux)
sudo cp cert.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

### Can't Find Vault

**Error**: `Vault path does not exist`

**Solution**: Verify path in config:
```bash
# Check the path exists
ls -la /Users/you/Documents/MyObsidianVault

# Ensure it's absolute path, not relative
# ✅ /Users/you/Documents/MyObsidianVault
# ❌ ~/Documents/MyObsidianVault  (use full path)
```

### Periodic Notes Not Working

**Problem**: Periodic notes endpoints return 404

**Solution**: Check configuration:

1. Ensure `obsidian.enabled: true` and `config_sync: true`
2. Verify Obsidian's periodic notes plugin is configured
3. Or manually configure in `config.yaml`:

```yaml
periodic_notes:
  daily:
    enabled: true
    format: "YYYY-MM-DD"
    folder: "Daily Notes/"
    template: "Templates/Daily.md"
```

## Reverting to Plugin

If you need to go back to the Obsidian plugin:

1. Stop markdown-vault:
   ```bash
   # If running manually
   Ctrl+C
   
   # If running as service
   sudo systemctl stop markdown-vault
   
   # If running in Docker
   docker-compose down
   ```

2. Re-enable Obsidian plugin:
   - Open Obsidian
   - Settings → Community Plugins → Local REST API
   - Toggle on

3. Update your applications to use the original API key (if you changed it)

## FAQ

### Q: Can I use markdown-vault without Obsidian installed?

**A**: Yes! markdown-vault is completely standalone. The `obsidian.enabled` option just means "respect Obsidian vault structure" - it doesn't require Obsidian to be installed.

### Q: Will markdown-vault modify my vault?

**A**: Only through API calls you make. It reads `.obsidian/` configuration but doesn't modify Obsidian settings. File operations happen only when you call the API.

### Q: Can I still use Obsidian with my vault?

**A**: Absolutely! markdown-vault just provides API access. You can use Obsidian normally. Enable `watch_files: true` to detect changes made by Obsidian.

### Q: What happens to active file tracking?

**A**: markdown-vault maintains its own active file state. It doesn't sync with Obsidian's currently open file. Use `/open/{filename}` to set the active file.

### Q: Do I need to migrate my API keys to all clients?

**A**: Only if you generated a new key. If you copied your Obsidian plugin key to markdown-vault, clients continue to work without changes.

### Q: Can markdown-vault handle multiple vaults?

**A**: Currently one vault per instance, but you can run multiple markdown-vault instances on different ports for different vaults.

## Getting Help

- Check the [README](../README.md) for general documentation
- See [PLAN.md](./PLAN.md) for implementation details
- Report issues on GitHub
- Ask in discussions

## Next Steps

After migration:

1. ✅ Close Obsidian (if you want) - API still works!
2. ✅ Set up automated backups of your vault
3. ✅ Configure markdown-vault as a system service (systemd/Docker)
4. ✅ Set up remote access (if needed) with proper security
5. ✅ Explore new automation possibilities without Obsidian running

---

**Welcome to always-on vault access!** 🎉
