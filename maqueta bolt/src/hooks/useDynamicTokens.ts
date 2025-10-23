import { useState, useEffect } from 'react';
import { UserContext } from './useContextCapture';
import { predictDesignTokens, DesignTokens } from '../utils/aiSimulation';

export function useDynamicTokens(context: UserContext) {
  const [tokens, setTokens] = useState<DesignTokens | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const applyTokens = async () => {
      setIsLoading(true);

      try {
        const predictedTokens = await predictDesignTokens(context);

        if (!isMounted) return;

        Object.entries(predictedTokens).forEach(([key, value]) => {
          document.documentElement.style.setProperty(key, value);
        });

        setTokens(predictedTokens);
      } catch (error) {
        console.error('Error applying design tokens:', error);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    applyTokens();

    return () => {
      isMounted = false;
    };
  }, [context.hour, context.isSmallScreen, context.prefersDark]);

  return { tokens, isLoading };
}
