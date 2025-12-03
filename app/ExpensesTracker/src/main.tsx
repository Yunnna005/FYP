import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import Dashboard from './pages/Dashboard.tsx'
import Template from './templates/Template.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Template >
      <Dashboard />
    </Template>
  </StrictMode>,
)
