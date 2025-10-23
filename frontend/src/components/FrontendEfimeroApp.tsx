/**
 * Aplicación principal del Frontend Efímero
 * Integra LoadingScreen + Demo principal con AdaptiveUIProvider
 */

'use client';

import { useState } from 'react';
import { LoadingScreen } from './LoadingScreen';
import { FrontendEfimeroDemo } from './FrontendEfimeroDemo';
import { AdaptiveUIProvider } from './adaptive/AdaptiveUIProvider';

export function FrontendEfimeroApp() {
  const [isLoading, setIsLoading] = useState(true);

  if (isLoading) {
    return <LoadingScreen onLoadingComplete={() => setIsLoading(false)} />;
  }

  return (
    <AdaptiveUIProvider>
      <FrontendEfimeroDemo />
    </AdaptiveUIProvider>
  );
}