import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import Gradient from '../components/Gradient';
import { TypeAnimation } from 'react-type-animation';
import { Camera, Sparkles, Zap } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();
  
  return (
    <div className="relative min-h-screen">
      <Gradient />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="bg-white bg-opacity-90 backdrop-filter backdrop-blur-lg rounded-lg shadow-xl p-8 max-w-lg w-full mx-4">
          <h1 className="text-3xl md:text-4xl font-bold text-center mb-6 text-gray-800">
            <TypeAnimation
              sequence={[
                'Welcome to Fabrik!',
                5000,
                'Welcome to FASHN_AI 😊',
                5000,
                'AI Fashion Magic ✨',
                5000,
              ]}
              wrapper="span"
              cursor={true}
              repeat={Infinity}
              className="inline-block"
            />
          </h1>
          
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="text-center p-4">
              <Camera className="w-6 h-6 mb-2 mx-auto text-[#02B5AB]" />
              <p className="text-sm font-medium text-gray-700">AI-Powered Fashion Shoots</p>
            </div>
            <div className="text-center p-4">
              <Sparkles className="w-6 h-6 mb-2 mx-auto text-[#02B5AB]" />
              <p className="text-sm font-medium text-gray-700">Any Model, Any Outfit</p>
            </div>
            <div className="text-center p-4">
              <Zap className="w-6 h-6 mb-2 mx-auto text-[#02B5AB]" />
              <p className="text-sm font-medium text-gray-700">Instant Results</p>
            </div>
          </div>

          <p className="text-center text-gray-600 mb-6 text-sm">
            Transform your fashion vision into reality using the FASHN AI platform.
          </p>
          
          <div className="text-center space-y-4">
            <Button
              onClick={() => navigate('/home')}
              className="w-full px-6 py-3 text-lg bg-[#02B5AB] text-white hover:bg-[#029990] transition-colors"
            >
              Get Started
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;