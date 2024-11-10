import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import Gradient from '../components/Gradient';
import { TypeAnimation } from 'react-type-animation';
import { BarChart2, Leaf, Zap } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <>
      {/* Background container */}
      <div className="fixed inset-0 bg-green-100" />
      
      {/* Main content wrapper */}
      <div className="relative h-screen overflow-hidden">
        <Gradient />
        <div className="relative z-10 h-screen flex items-center">
          {/* Content container */}
          <div className="w-full max-w-[1500px] px-12 mx-auto">
            <div className="flex flex-col lg:flex-row gap-24">
              {/* Left side content */}
              <div className="flex-1 flex flex-col justify-center mb-36">
                <h1 className="text-6xl font-bold text-gray-800 mb-6">
                  <span className="whitespace-nowrap">Make sustainable choices.</span>
                  <br />
                  <span className="text-[#02B5AB]">Save money.</span>
                </h1>
                <p className="text-xl text-gray-700 mb-8 max-w-xl">
                  Discover how switching to renewable energy can benefit both your wallet and the planet.
                </p>
              </div>

              {/* Right side card */}
              <div className="flex-1">
                <div className="bg-white bg-opacity-90 backdrop-filter backdrop-blur-lg rounded-lg shadow-xl p-8">
                  {/* Logo */}
                  <div className="flex justify-center mb-6">
                    <img
                      src="/eco_logo_notext.png"
                      alt="ECOnomics Logo"
                      className="max-w-[100px] max-h-[100px]"
                    />
                  </div>

                  <h2 className="text-3xl font-bold text-center mb-6 text-gray-800">
                    <TypeAnimation
                      sequence={[
                        'Welcome to ECOnomics!',
                        3000,
                        'Calculate Your Savings',
                        3000,
                        'Reduce Your Carbon Footprint',
                        3000,
                      ]}
                      wrapper="span"
                      cursor={true}
                      repeat={Infinity}
                      className="inline-block"
                    />
                  </h2>

                  <div className="grid grid-cols-1 gap-6 mb-8">
                    <div className="flex items-center p-4 bg-green-50 rounded-lg">
                      <BarChart2 className="w-8 h-8 mr-4 text-[#02B5AB]" />
                      <div>
                        <h3 className="font-medium text-gray-800">Smart Analytics</h3>
                        <p className="text-sm text-gray-600">Calculate potential savings and ROI from renewable energy</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center p-4 bg-green-50 rounded-lg">
                      <Leaf className="w-8 h-8 mr-4 text-[#02B5AB]" />
                      <div>
                        <h3 className="font-medium text-gray-800">Environmental Impact</h3>
                        <p className="text-sm text-gray-600">Track your CO2 reduction and environmental benefits</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center p-4 bg-green-50 rounded-lg">
                      <Zap className="w-8 h-8 mr-4 text-[#02B5AB]" />
                      <div>
                        <h3 className="font-medium text-gray-800">AI-Powered Insights</h3>
                        <p className="text-sm text-gray-600">Get personalized recommendations for your energy needs</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Button
                      onClick={() => navigate('/home')}
                      className="w-full px-6 py-3 text-lg bg-[#02B5AB] text-white hover:bg-[#029990] transition-colors"
                    >
                      Calculate Your Savings
                    </Button>
                    <Button
                      onClick={() => navigate('/chatbot')}
                      className="w-full px-6 py-3 text-lg border-2 border-[#02B5AB] text-[#02B5AB] bg-transparent hover:bg-[#02B5AB] hover:text-white transition-colors"
                    >
                      Chat with AI Assistant
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default LandingPage;