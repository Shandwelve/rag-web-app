# Client Application

React-based frontend for the RAG Web Application, providing an intuitive interface for document management and AI-powered question answering.

## Overview

The client application is a modern React single-page application built with TypeScript and Vite. It provides a complete user interface for interacting with the RAG backend, including document upload, question answering (text and voice), user management, and analytics.

## Tech Stack

- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui (built on Radix UI primitives)
- **Icons**: Lucide React
- **State Management**: React Context API
- **HTTP Client**: Fetch API with custom wrapper
- **File Upload**: react-dropzone

## Project Structure

```
client/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── textarea.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── scroll-area.tsx
│   │   │   └── skeleton.tsx
│   │   ├── AdminPanel.tsx
│   │   ├── FileList.tsx
│   │   ├── FileUpload.tsx
│   │   ├── LoginButton.tsx
│   │   ├── LogoutButton.tsx
│   │   ├── ProtectedRoute.tsx
│   │   ├── QuestionHistory.tsx
│   │   ├── RAGChat.tsx
│   │   └── RAGStats.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx
│   ├── services/
│   │   ├── authService.ts
│   │   ├── fileService.ts
│   │   ├── ragService.ts
│   │   └── userService.ts
│   ├── utils/
│   │   └── api.ts
│   ├── lib/
│   │   └── utils.ts
│   ├── assets/
│   │   └── react.svg
│   ├── App.tsx
│   ├── App.css
│   ├── main.tsx
│   └── index.css
├── public/
│   └── vite.svg
├── dist/
├── index.html
├── package.json
├── package-lock.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
├── components.json
├── eslint.config.js
└── README.md
```

### Directory Descriptions

**src/components/** - React components
- **ui/** - Reusable UI components built with Radix UI (shadcn/ui)
- **AdminPanel.tsx** - Admin user management interface
- **FileList.tsx** - File listing and management component
- **FileUpload.tsx** - File upload component with drag-and-drop
- **LoginButton.tsx** - Authentication login component
- **LogoutButton.tsx** - Authentication logout component
- **ProtectedRoute.tsx** - Route protection wrapper with role-based access
- **QuestionHistory.tsx** - Question-answer history viewer
- **RAGChat.tsx** - Main chat interface for Q&A interactions
- **RAGStats.tsx** - Statistics dashboard component

**src/contexts/** - React contexts for global state
- **AuthContext.tsx** - Authentication state management

**src/services/** - API service clients
- **authService.ts** - Authentication API integration
- **fileService.ts** - File management API integration
- **ragService.ts** - RAG API integration
- **userService.ts** - User management API integration

**src/utils/** - Utility functions
- **api.ts** - API fetch wrapper with error handling

**src/lib/** - Library utilities
- **utils.ts** - Helper functions (e.g., `cn` for Tailwind class merging)

**src/assets/** - Static assets
- Images, icons, and other static files

**Root files:**
- **App.tsx** - Main application component
- **main.tsx** - Application entry point
- **index.css** - Global styles (Tailwind CSS)
- **index.html** - HTML template
- **vite.config.ts** - Vite build configuration
- **tsconfig.json** - TypeScript configuration
- **components.json** - shadcn/ui component configuration

## Setup

### Prerequisites

- Node.js 18+ and npm
- Running backend API server (see [API README](../api/README.md))

### Installation

1. Navigate to the client directory:

```bash
cd client
```

2. Install dependencies:

```bash
npm install
```

3. Configure the API endpoint (if different from default):

The API base URL is configured in `src/utils/api.ts`. By default, it points to `http://localhost:8000`. Update this if your API runs on a different port or host.

4. Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Features

### Authentication

- **WorkOS Integration**: Secure authentication via WorkOS SSO
- **Role-Based Access**: Different interfaces for admin and regular users
- **Session Management**: Automatic session handling and refresh

### Document Management (Admin Only)

- **File Upload**: Drag-and-drop or click to upload PDF/DOCX files
- **File List**: View all uploaded documents with metadata
- **File Download**: Download uploaded files
- **File Deletion**: Remove documents from the system

### RAG Chat Interface

- **Text Questions**: Ask questions about uploaded documents
- **Voice Input**: Record audio questions for voice-based interaction
- **Session Tracking**: Maintain conversation context across questions
- **Source Citations**: View document sources for answers
- **Image Support**: Display images from documents when relevant
- **Confidence Scores**: See confidence levels for generated answers

### Question History (Admin Only)

- **History View**: Browse all question-answer pairs
- **Session Filtering**: Filter by conversation session
- **Question Management**: Delete questions from history

### Statistics Dashboard (Admin Only)

- **Usage Metrics**: View total questions, answers, and average confidence
- **User Analytics**: Track user engagement and activity

### Admin Panel

- **User Management**: Create, view, update, and delete users
- **Role Assignment**: Assign admin or user roles
- **User List**: View all registered users

## Available Scripts

### Development

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

### Production Build

```bash
# Build optimized production bundle
npm run build
```

The built files will be in the `dist/` directory, ready for deployment.

## API Integration

The client communicates with the backend API through service classes:

### Authentication Service (`authService.ts`)

- `getLoginUrl()` - Get WorkOS authorization URL
- `getCurrentUser()` - Get current authenticated user
- `logout()` - Logout user

### File Service (`fileService.ts`)

- `uploadFile(file)` - Upload a document
- `getFiles()` - Get all uploaded files
- `getFile(fileId)` - Get file details
- `downloadFile(fileId)` - Download a file
- `deleteFile(fileId)` - Delete a file

### RAG Service (`ragService.ts`)

- `askQuestion(question, sessionId?)` - Ask a text question
- `askVoiceQuestion(audioFile, sessionId?)` - Ask a voice question
- `getQuestionHistory(limit?)` - Get question history
- `getSessionHistory(sessionId)` - Get session-specific history
- `deleteQuestion(questionId)` - Delete a question
- `getStats()` - Get statistics

### User Service (`userService.ts`)

- `getUsers()` - Get all users
- `getUser(userId)` - Get user details
- `createUser(userData)` - Create a new user
- `updateUser(userId, userData)` - Update a user
- `deleteUser(userId)` - Delete a user

## Component Architecture

### Main Components

- **App.tsx**: Main application container with routing and tab navigation
- **RAGChat.tsx**: Chat interface for Q&A interactions
- **FileUpload.tsx**: File upload component with drag-and-drop
- **FileList.tsx**: File listing with download and delete actions
- **AdminPanel.tsx**: User management interface
- **QuestionHistory.tsx**: Question-answer history viewer
- **RAGStats.tsx**: Statistics dashboard

### UI Components

Built on shadcn/ui components (which use Radix UI primitives):
- Button, Card, Input, Textarea
- Badge, ScrollArea, Skeleton
- Fully accessible and customizable
- Components are copied directly into the project (not installed as a dependency)

**About shadcn/ui**: shadcn/ui is a collection of reusable components built on top of Radix UI primitives and styled with Tailwind CSS. Unlike traditional component libraries, shadcn/ui components are copied directly into your project's `src/components/ui/` directory, giving you full control to customize them. The components are configured via `components.json` and use Radix UI primitives (like `@radix-ui/react-slot`) for accessibility and functionality.

## State Management

The application uses React Context API for state management:

- **AuthContext**: Manages authentication state, user information, and auth methods
- Local component state for UI-specific data
- Service classes handle API interactions

## Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Custom CSS**: Global styles in `index.css`
- **Responsive Design**: Mobile-first responsive layouts
- **Dark Mode Support**: Ready for theme customization

## Environment Configuration

The API base URL is configured in `src/utils/api.ts`. To change it:

```typescript
const API_BASE_URL = 'http://your-api-url:port'
```

## Development Workflow

1. **Start Backend**: Ensure the API server is running (see [API README](../api/README.md))
2. **Start Frontend**: Run `npm run dev`
3. **Hot Reload**: Changes automatically reload in the browser
4. **Type Checking**: TypeScript provides real-time type checking
5. **Linting**: ESLint ensures code quality

## Building for Production

```bash
# Build production bundle
npm run build
```

The production build includes:
- Minified JavaScript and CSS
- Optimized assets
- Tree-shaking to remove unused code
- Code splitting for optimal loading

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues

- Verify the backend API is running
- Check API base URL in `src/utils/api.ts`
- Verify CORS settings in backend
- Check browser console for errors

### Authentication Issues

- Ensure WorkOS credentials are configured in backend
- Check redirect URI matches WorkOS configuration
- Verify cookies are enabled in browser
- Clear browser cache and cookies if needed

### Build Issues

- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check Node.js version compatibility

### File Upload Issues

- Verify file size limits
- Ensure file type is PDF or DOCX
- Check network connectivity
- Verify backend storage directory exists

## Performance Optimization

- Code splitting for route-based chunks
- Lazy loading for heavy components
- Optimized bundle size through tree-shaking
- Efficient re-renders with React hooks
- Memoization where appropriate

## Accessibility

- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- Focus management
- Semantic HTML structure

## Contributing

When contributing to the client:

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Maintain component prop types
4. Follow existing code style
5. Add error handling for API calls
6. Ensure responsive design
7. Test across different browsers
