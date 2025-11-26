import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { SupabaseProvider } from './contexts/SupabaseContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SupabaseProvider>
      <App />
    </SupabaseProvider>
  </StrictMode>,
)
