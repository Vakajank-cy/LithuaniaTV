import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [currentProgram, setCurrentProgram] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const videoRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    fetchChannels();
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const fetchChannels = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/channels`);
      const data = await response.json();
      setChannels(data.channels);
      if (data.channels.length > 0) {
        setSelectedChannel(data.channels[0]);
      }
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching channels:', error);
      setIsLoading(false);
    }
  };

  const handleChannelSelect = async (channel) => {
    setSelectedChannel(channel);
    setIsPlaying(false);
    
    // Fetch current program for the channel
    try {
      const response = await fetch(`${BACKEND_URL}/api/channels/${channel.id}/programs`);
      const data = await response.json();
      if (data.programs.length > 0) {
        setCurrentProgram(data.programs[0]);
      }
    } catch (error) {
      console.error('Error fetching programs:', error);
    }
  };

  const handlePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(e => {
          console.log('Autoplay prevented:', e);
        });
      }
      setIsPlaying(!isPlaying);
    }
  };

  const formatStreamUrl = (url) => {
    // For demo purposes, using a sample video stream
    // In production, you would use the actual streaming URLs from LRT/LNK
    return 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl flex items-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          <span>Loading Lithuanian TV...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-red-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">LT</span>
              </div>
              <h1 className="text-white text-2xl font-bold">Lithuanian TV</h1>
            </div>
            <div className="text-white/80 text-sm">
              <span className="hidden sm:inline">🔴 LIVE • </span>
              {new Date().toLocaleTimeString()}
            </div>
          </div>
        </div>
      </header>

      <div className={`container mx-auto px-4 py-6 ${isMobile ? 'space-y-6' : 'grid grid-cols-4 gap-6'}`}>
        {/* Main Video Player */}
        <div className={`${isMobile ? 'order-1' : 'col-span-3'} space-y-4`}>
          <div className="bg-black rounded-xl overflow-hidden shadow-2xl">
            <div className="aspect-video relative">
              <video
                ref={videoRef}
                className="w-full h-full object-cover"
                poster="https://images.unsplash.com/photo-1597432683665-4988f859868f?w=800"
                controls
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
              >
                {selectedChannel && (
                  <source src={formatStreamUrl(selectedChannel.stream_url)} type="video/mp4" />
                )}
                Your browser does not support the video tag.
              </video>
              
              {!isPlaying && (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                  <button
                    onClick={handlePlay}
                    className="bg-white/20 hover:bg-white/30 rounded-full p-6 transition-all duration-200 backdrop-blur-sm"
                  >
                    <svg className="w-16 h-16 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Current Channel Info */}
          {selectedChannel && (
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-white">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <img 
                    src={selectedChannel.logo} 
                    alt={selectedChannel.name}
                    className="w-16 h-16 rounded-lg object-cover"
                  />
                  <div>
                    <h2 className="text-2xl font-bold">{selectedChannel.name}</h2>
                    <p className="text-white/80">{selectedChannel.description}</p>
                  </div>
                </div>
                <span className="bg-red-500 px-3 py-1 rounded-full text-sm font-medium">
                  🔴 LIVE
                </span>
              </div>
              
              {currentProgram && (
                <div className="border-t border-white/20 pt-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="font-semibold text-lg">{currentProgram.title}</h3>
                      <p className="text-white/80 text-sm">{currentProgram.description}</p>
                    </div>
                    <div className="text-right text-sm text-white/80">
                      <div>{currentProgram.start_time} - {currentProgram.end_time}</div>
                      <div className="text-xs">{currentProgram.genre}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Channel List */}
        <div className={`${isMobile ? 'order-2' : 'col-span-1'}`}>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <h3 className="text-white text-lg font-semibold mb-4 flex items-center">
              <span className="mr-2">📺</span>
              Channels
            </h3>
            
            <div className="space-y-2">
              {channels.map((channel) => (
                <button
                  key={channel.id}
                  onClick={() => handleChannelSelect(channel)}
                  className={`w-full p-3 rounded-lg transition-all duration-200 text-left ${
                    selectedChannel?.id === channel.id
                      ? 'bg-blue-500/30 border-2 border-blue-400'
                      : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <img 
                      src={channel.logo} 
                      alt={channel.name}
                      className="w-10 h-10 rounded-lg object-cover"
                    />
                    <div className="flex-1">
                      <div className="text-white font-medium">{channel.name}</div>
                      <div className="text-white/60 text-xs">{channel.category}</div>
                    </div>
                    {channel.is_live && (
                      <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    )}
                  </div>
                </button>
              ))}
            </div>

            {/* Instructions */}
            <div className="mt-6 p-4 bg-yellow-500/20 rounded-lg">
              <h4 className="text-yellow-300 font-medium text-sm mb-2">📱 How to watch:</h4>
              <ul className="text-yellow-200/80 text-xs space-y-1">
                <li>• Select a channel from the list</li>
                <li>• Click play to start streaming</li>
                <li>• Works on phone and TV!</li>
                <li>• Swipe for mobile navigation</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 mt-12">
        <div className="container mx-auto px-4 py-6">
          <div className="text-center text-white/60 text-sm">
            <p>🇱🇹 Lithuanian TV Streaming • Personal Use • {new Date().getFullYear()}</p>
            <p className="mt-2 text-xs">Official streams from LRT and LNK broadcasters</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;