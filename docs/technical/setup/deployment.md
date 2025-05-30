## Deployment Scenarios

### Local Development
```yaml
# config/config.yaml
system:
  name: "ARABLE Development"
  log_level: "DEBUG"

logging:
  level: "DEBUG"
  file: "logs/arable-dev.log"
```

### RSi Production
```yaml
# config/config.yaml  
system:
  name: "ARABLE Production - RSi Visual Systems"
  log_level: "INFO"

logging:
  level: "INFO" 
  file: "/var/log/arable/arable.log"
```

### Testing Environment
```yaml
# config/test.yaml
system:
  name: "ARABLE Testing"
  log_level: "DEBUG"

monday:
  # Use test boards
  master_board_id: 999999999
  template_board_id: 888888888
```

**Using different configs**:
```bash
# Specify config file
arable project 12345 --config config/test.yaml

# Or set environment variable
export ARABLE_CONFIG_PATH=config/test.yaml
arable project 12345
```

---

## Advanced Configuration

### Multiple Environments

**Structure**:
```
config/
├── config.yaml          # Default/production
├── development.yaml     # Development overrides
├── testing.yaml         # Testing configuration
└── config.example.yaml  # Template
```

**Usage**:
```bash
# Development
arable project 12345 --config config/development.yaml

# Testing  
arable project 12345 --config config/testing.yaml
```

### Environment Variable Substitution

Configuration supports environment variable substitution:
```yaml
monday:
  api_token: "${MONDAY_API_TOKEN}"              # Required
  backup_token: "${MONDAY_BACKUP_TOKEN:-}"     # Optional with default
  rate_limit: "${MONDAY_RATE_LIMIT:-60}"       # Default to 60
```

### Logging Configuration

**Log Levels**:
- `DEBUG`: Detailed information for debugging
- `INFO`: General operational information  
- `WARNING`: Warning messages
- `ERROR`: Error messages only

**Log Destinations**:
```yaml
logging:
  level: "INFO"
  file: "logs/arable.log"        # File logging
  console: true                  # Also log to console
  max_size_mb: 50               # Rotate at 50MB
  backup_count: 3               # Keep 3 backup files
```

---