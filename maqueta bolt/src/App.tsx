import { useState } from 'react';
import { LoadingScreen } from './components/LoadingScreen';
import { CarShowcase } from './components/CarShowcase';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  if (isLoading) {
    return <LoadingScreen onLoadingComplete={() => setIsLoading(false)} />;
  }

  return <CarShowcase />;
}

export default App;
