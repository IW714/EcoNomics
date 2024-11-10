import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import HomePage from './pages/HomePage'
import ChatbotPage from './pages/ChatbotPage'
import './App.css'

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/home" element={<HomePage />} />
      <Route path="/chatbot" element={<ChatbotPage />} />
    </Routes>
  )
}

export default App
