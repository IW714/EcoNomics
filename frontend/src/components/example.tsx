import { useState, useEffect } from 'react';

const ThreeDText = () => {
  const [rotation, setRotation] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [lastPosition, setLastPosition] = useState({ x: 0, y: 0 });
  const [message, setMessage] = useState<string>('');

  useEffect(() => {
    fetch('http://127.0.0.1:8000')
        .then((response) => response.json())
        .then((data) => {
            setMessage(data.Hello);
        })
        .catch((error) => {
            console.error('Error fetching data:', error);
        });
}, []);

  const handleMouseDown = (e: { clientX: any; clientY: any; }) => {
    setIsDragging(true);
    setLastPosition({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: { clientX: number; clientY: number; }) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - lastPosition.x;
    const deltaY = e.clientY - lastPosition.y;
    
    setRotation({
      x: rotation.x + deltaY * 0.5,
      y: rotation.y + deltaX * 0.5
    });
    
    setLastPosition({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div 
      className="w-full h-96 bg-gray-900 rounded-lg cursor-move overflow-hidden"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div 
        className="w-full h-full flex items-center justify-center"
        style={{
          perspective: '1000px'
        }}
      >
        <div
          className="text-6xl font-bold text-white"
          style={{
            transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`,
            transformStyle: 'preserve-3d'
          }}
        >
          {message}
        </div>
      </div>
      <div className="absolute bottom-4 left-0 right-0 text-center text-gray-400 text-sm">
        Click and drag to rotate
      </div>
    </div>
  );
};

export default ThreeDText;