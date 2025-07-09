# Utah Tech IAP Advisor - Frontend

A modern React/Next.js frontend for the Utah Tech Individualized Academic Plan (IAP) Advisor system.

## Features

### 🎯 Core Functionality
- **Interactive Chat Interface** - Natural conversation with AI advisor
- **Real-time MCP Integration** - Seamless connection to 28+ MCP tools
- **IAP Progress Dashboard** - Visual tracking of degree requirements
- **Course Search & Discovery** - Find courses across Utah Tech's catalog
- **Market Research Integration** - Career viability analysis
- **Credit Analysis** - Track progress toward 120 credit requirement

### 💬 Chat Capabilities
- Course search and recommendations
- Degree requirement validation
- Market research for emphasis areas
- IAP template creation and editing
- Prerequisites checking
- Credit calculation and analysis

### 📊 Dashboard Features
- IAP completion progress (visual percentage)
- Requirements checklist with status indicators
- Student information display
- Concentration areas management
- Quick action buttons
- Helpful tips and guidance

## Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Date Handling**: date-fns

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Utah Tech MCP Server running on port 8051

### Installation

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your MCP server URL
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   ```
   http://localhost:3000
   ```

## Project Structure

```
frontend/
├── app/
│   ├── components/          # React components
│   │   ├── ChatInterface.tsx    # Main chat component
│   │   ├── Dashboard.tsx        # Progress dashboard
│   │   ├── Header.tsx           # App header
│   │   └── MessageBubble.tsx    # Chat message display
│   ├── api/
│   │   └── chat/
│   │       └── route.ts         # Chat API endpoint
│   ├── types.ts             # TypeScript interfaces
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page
├── public/                  # Static assets
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json          # TypeScript configuration
└── next.config.js         # Next.js configuration
```

## API Integration

The frontend connects to the Utah Tech MCP Server through:

- **Chat API** (`/api/chat`) - Processes user messages and orchestrates MCP tools
- **MCP Tools Integration** - Automatic tool selection based on message content
- **Real-time Updates** - Live IAP data updates from tool results

### Supported MCP Tools

- `search_courses` - Course catalog search
- `search_degree_programs` - Program discovery
- `calculate_credits` - Credit hour analysis
- `conduct_market_research` - Career viability research
- `validate_iap_requirements` - BIS degree validation
- `generate_iap_suggestions` - AI-powered content generation
- `create_iap_template` - IAP document creation
- `check_prerequisites` - Course prerequisite analysis

## User Experience

### Chat Flow
1. **Welcome Message** - AI introduces itself and capabilities
2. **Natural Conversation** - Students ask questions in plain English
3. **Tool Orchestration** - System automatically uses relevant MCP tools
4. **Rich Responses** - AI provides detailed answers with tool results
5. **Progress Updates** - Dashboard reflects changes in real-time

### Example Interactions
- "I want to create an emphasis in Psychology and Digital Media"
- "Help me find upper-division psychology courses"
- "What are the BIS degree requirements?"
- "Check if my course plan meets graduation requirements"

## Deployment

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm start
```

### Environment Variables
- `MCP_SERVER_URL` - URL of the Utah Tech MCP Server
- `NEXT_PUBLIC_APP_NAME` - Application display name
- `NEXT_PUBLIC_APP_VERSION` - Version number

## Contributing

1. Follow TypeScript best practices
2. Use Tailwind CSS for styling
3. Maintain component modularity
4. Test chat interactions thoroughly
5. Ensure MCP tool integration works correctly

## Support

For issues related to:
- **Frontend bugs** - Check browser console and network requests
- **MCP integration** - Verify MCP server is running on port 8051
- **Chat responses** - Check API route logs and tool execution
- **UI/UX issues** - Review component props and state management
