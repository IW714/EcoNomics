import { useContext } from 'react';
import { Switch } from '@/components/ui/switch';
import { ThemeContext } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
  const { isDarkMode, toggleTheme } = useContext(ThemeContext);

  return (
    <div className="flex items-center">
      <span className="mr-2 text-sm">{isDarkMode ? 'Dark' : 'Light'} Mode</span>
      <Switch checked={isDarkMode} onCheckedChange={toggleTheme} />
    </div>
  );
}
