# Configuration Guide

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# API Keys (required - at least one AI provider)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# AWS Configuration (required for deployment)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# Database
DATABASE_URL=sqlite+aiosqlite:///./shipdb.db

# API Configuration
API_TITLE=ShipDB API
API_VERSION=0.1.0

# AI Model Configuration
OPENAI_MODEL=gpt-4
GEMINI_MODEL=gemini-1.5-flash
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620
```

## Getting API Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key to `OPENAI_API_KEY`

### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Create a new API key
3. Copy the key to `ANTHROPIC_API_KEY`

### Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Create a new API key
3. Copy the key to `GEMINI_API_KEY`

### AWS Credentials
1. Go to AWS IAM Console
2. Create a new user with programmatic access
3. Attach policies: `AmazonDynamoDBFullAccess`, `AmazonRDSFullAccess`, `AmazonEC2FullAccess`
4. Copy Access Key ID and Secret Access Key to the respective variables

## Notes

- You only need one AI provider API key (OpenAI, Anthropic, or Gemini)
- AWS credentials are required for database deployment
- The application will work without AWS credentials for schema generation only
