import { useState, useEffect } from 'react';

export interface UserContext {
  hour: number;
  screenWidth: number;
  screenHeight: number;
  prefersDark: boolean;
  isNight: boolean;
  isSmallScreen: boolean;
  timestamp: number;
}

export function useContextCapture() {
  const [context, setContext] = useState<UserContext>({
    hour: new Date().getHours(),
    screenWidth: window.innerWidth,
    screenHeight: window.innerHeight,
    prefersDark: window.matchMedia('(prefers-color-scheme: dark)').matches,
    isNight: false,
    isSmallScreen: false,
    timestamp: Date.now(),
  });

  useEffect(() => {
    const updateContext = () => {
      const hour = new Date().getHours();
      const screenWidth = window.innerWidth;
      const screenHeight = window.innerHeight;
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      const isNight = hour < 7 || hour > 19;
      const isSmallScreen = screenWidth < 768;

      setContext({
        hour,
        screenWidth,
        screenHeight,
        prefersDark,
        isNight,
        isSmallScreen,
        timestamp: Date.now(),
      });
    };

    updateContext();

    const resizeObserver = new ResizeObserver(updateContext);
    resizeObserver.observe(document.body);

    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleDarkModeChange = () => updateContext();
    darkModeQuery.addEventListener('change', handleDarkModeChange);

    const hourInterval = setInterval(updateContext, 60000);

    return () => {
      resizeObserver.disconnect();
      darkModeQuery.removeEventListener('change', handleDarkModeChange);
      clearInterval(hourInterval);
    };
  }, []);

  return context;
}
