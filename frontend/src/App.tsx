import { Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import HomePage from './pages/HomePage'
import ThemeToggle from './components/ThemeToggle'
import './App.css'

function App() {
  return (
    <div>
      {/* Header or Navbar */}
      <header className="flex justify-between items-center p-4">
        {/* Other header content */}
        <ThemeToggle />
      </header>
      {/* Routes */}
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/home" element={<HomePage />} />
      </Routes>
    </div>
  );
}

export default App
