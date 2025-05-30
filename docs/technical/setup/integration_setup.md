## Integration Setup

### Monday.com Setup

**1. Get API Token**
- Go to Monday.com > Admin > API
- Generate new token with full permissions
- Add to `.env` as `MONDAY_API_TOKEN`

**2. Find Board and Folder IDs**

Use Monday.com URLs to find IDs:
```
https://mycompany.monday.com/boards/123456789
                              ^^^^^^^^^^^
                              This is your board ID

https://mycompany.monday.com/folders/111222333
                               ^^^^^^^^^^^  
                               This is your folder ID
```

**3. Map Column IDs**

Find column IDs in Monday.com:
- Go to board > Settings > Columns
- Each column has an ID (usually like "text", "text5", "status4", etc.)
- Update `config.yaml` with correct column mappings

### Google Sheets Setup

**1. Create Service Account**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project or select existing
- Enable Google Sheets API
- Create service account
- Download JSON credentials file

**2. Install Credentials**
```bash
# Place credentials file in credentials directory
cp ~/Downloads/service-account-key.json credentials/rsinet-service-account.json

# Update config.yaml with correct path
```

**3. Grant Sheet Access**
- Open your Google Sheet
- Share with service account email (found in JSON file)
- Give "Editor" permissions

**4. Verify Sheet Structure**

ARABLE expects these columns in Google Sheets:
- `ProjectNumber`
- `ProjectName` 
- `CustomerShortname`
- `MilestoneID`
- `MileStoneType`
- `DateOfMilestone`

### Zoho CRM Setup (Optional)

Currently uses CSV exports rather than API:
```bash
# Place CRM exports in data/crm/backups/
# Files like: Accounts_001.csv, Contacts_001.csv, etc.
```

---