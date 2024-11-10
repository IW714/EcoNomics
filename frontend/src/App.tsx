import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import HomePage from './pages/HomePage'
import ThemeToggle from './components/ThemeToggle'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header or Navbar would go here */}
      <header className="flex justify-between items-center p-4 bg-background">
        <ThemeToggle />
      </header>
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/home" element={<HomePage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App
