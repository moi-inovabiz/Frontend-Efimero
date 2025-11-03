/**
 * Browser Detection Utilities
 * Detecta sistema operativo, navegador, dispositivo y capacidades
 * Sin dependencias externas - todo basado en APIs nativas del navegador
 */

export interface BrowserInfo {
  name: string;
  version: string;
  major_version: number;
}

export interface OSInfo {
  name: string;
  version: string;
}

export interface DeviceInfo {
  type: 'mobile' | 'tablet' | 'desktop';
  is_mobile_os: boolean;
  is_touch_device: boolean;
}

/**
 * Detecta el navegador y su versión desde el user agent
 */
export function getBrowser(userAgent?: string): BrowserInfo {
  const ua = userAgent || (typeof navigator !== 'undefined' ? navigator.userAgent : '');
  
  // Edge (Chromium)
  if (/Edg\//.test(ua)) {
    const match = ua.match(/Edg\/(\d+)\.(\d+)/);
    return {
      name: 'Edge',
      version: match ? `${match[1]}.${match[2]}` : 'unknown',
      major_version: match ? parseInt(match[1]) : 0
    };
  }
  
  // Chrome
  if (/Chrome\//.test(ua) && !/Edg\//.test(ua)) {
    const match = ua.match(/Chrome\/(\d+)\.(\d+)/);
    return {
      name: 'Chrome',
      version: match ? `${match[1]}.${match[2]}` : 'unknown',
      major_version: match ? parseInt(match[1]) : 0
    };
  }
  
  // Safari
  if (/Safari\//.test(ua) && !/Chrome\//.test(ua)) {
    const match = ua.match(/Version\/(\d+)\.(\d+)/);
    return {
      name: 'Safari',
      version: match ? `${match[1]}.${match[2]}` : 'unknown',
      major_version: match ? parseInt(match[1]) : 0
    };
  }
  
  // Firefox
  if (/Firefox\//.test(ua)) {
    const match = ua.match(/Firefox\/(\d+)\.(\d+)/);
    return {
      name: 'Firefox',
      version: match ? `${match[1]}.${match[2]}` : 'unknown',
      major_version: match ? parseInt(match[1]) : 0
    };
  }
  
  // Opera
  if (/OPR\//.test(ua)) {
    const match = ua.match(/OPR\/(\d+)\.(\d+)/);
    return {
      name: 'Opera',
      version: match ? `${match[1]}.${match[2]}` : 'unknown',
      major_version: match ? parseInt(match[1]) : 0
    };
  }
  
  // Internet Explorer
  if (/MSIE|Trident/.test(ua)) {
    const match = ua.match(/(?:MSIE |rv:)(\d+)/);
    return {
      name: 'IE',
      version: match ? match[1] : 'unknown',
      major_version: match ? parseInt(match[1]) : 0
    };
  }
  
  return {
    name: 'Unknown',
    version: 'unknown',
    major_version: 0
  };
}

/**
 * Detecta el sistema operativo y su versión
 */
export function getOS(userAgent?: string): OSInfo {
  const ua = userAgent || (typeof navigator !== 'undefined' ? navigator.userAgent : '');
  
  // iOS
  if (/iPad|iPhone|iPod/.test(ua)) {
    const match = ua.match(/OS (\d+)[._](\d+)(?:[._](\d+))?/);
    return {
      name: 'iOS',
      version: match ? `${match[1]}.${match[2]}${match[3] ? `.${match[3]}` : ''}` : 'unknown'
    };
  }
  
  // Android
  if (/Android/.test(ua)) {
    const match = ua.match(/Android (\d+(?:\.\d+)?)/);
    return {
      name: 'Android',
      version: match ? match[1] : 'unknown'
    };
  }
  
  // Windows
  if (/Windows NT/.test(ua)) {
    const match = ua.match(/Windows NT (\d+\.\d+)/);
    const versionMap: Record<string, string> = {
      '10.0': '10/11',
      '6.3': '8.1',
      '6.2': '8',
      '6.1': '7',
      '6.0': 'Vista',
      '5.1': 'XP'
    };
    const version = match ? (versionMap[match[1]] || match[1]) : 'unknown';
    return {
      name: 'Windows',
      version
    };
  }
  
  // macOS
  if (/Mac OS X/.test(ua)) {
    const match = ua.match(/Mac OS X (\d+)[._](\d+)(?:[._](\d+))?/);
    return {
      name: 'macOS',
      version: match ? `${match[1]}.${match[2]}${match[3] ? `.${match[3]}` : ''}` : 'unknown'
    };
  }
  
  // Linux
  if (/Linux/.test(ua)) {
    return {
      name: 'Linux',
      version: 'unknown'
    };
  }
  
  // Chrome OS
  if (/CrOS/.test(ua)) {
    return {
      name: 'Chrome OS',
      version: 'unknown'
    };
  }
  
  return {
    name: 'Unknown',
    version: 'unknown'
  };
}

/**
 * Detecta el tipo de dispositivo
 */
export function getDeviceType(userAgent?: string): DeviceInfo {
  const ua = userAgent || (typeof navigator !== 'undefined' ? navigator.userAgent : '');
  const uaLower = ua.toLowerCase();
  
  // Detectar tablet
  const isTablet = /(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua);
  
  // Detectar móvil
  const isMobile = /mobile|iphone|ipod|blackberry|iemobile|opera mini|wpdesktop/i.test(ua);
  
  // Detectar OS móvil
  const isMobileOS = /iOS|Android|Windows Phone/.test(getOS(ua).name);
  
  // Detectar touch
  const isTouchDevice = typeof window !== 'undefined' && (
    'ontouchstart' in window ||
    navigator.maxTouchPoints > 0 ||
    (navigator as any).msMaxTouchPoints > 0
  );
  
  let type: 'mobile' | 'tablet' | 'desktop';
  
  if (isTablet) {
    type = 'tablet';
  } else if (isMobile) {
    type = 'mobile';
  } else {
    type = 'desktop';
  }
  
  return {
    type,
    is_mobile_os: isMobileOS,
    is_touch_device: isTouchDevice
  };
}

/**
 * Verifica si el navegador es moderno (últimas 2 versiones)
 */
export function isModernBrowser(browser?: BrowserInfo): boolean {
  const browserInfo = browser || getBrowser();
  
  const minVersions: Record<string, number> = {
    'Chrome': 110,
    'Edge': 110,
    'Safari': 16,
    'Firefox': 110,
    'Opera': 95
  };
  
  const minVersion = minVersions[browserInfo.name];
  if (!minVersion) return false;
  
  return browserInfo.major_version >= minVersion;
}

/**
 * Obtiene información de la conexión de red
 */
export function getConnectionInfo() {
  if (typeof navigator === 'undefined' || !(navigator as any).connection) {
    return {
      type: 'unknown',
      effectiveType: 'unknown',
      downlink: 0,
      rtt: 0,
      saveData: false
    };
  }
  
  const conn = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
  
  return {
    type: conn.type || 'unknown',
    effectiveType: conn.effectiveType || 'unknown',
    downlink: conn.downlink || 0,
    rtt: conn.rtt || 0,
    saveData: conn.saveData || false
  };
}

/**
 * Obtiene el timezone del usuario
 */
export function getTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  } catch {
    return 'UTC';
  }
}

/**
 * Obtiene el locale/idioma del usuario
 */
export function getLocale(): { primary: string; languages: string[] } {
  if (typeof navigator === 'undefined') {
    return { primary: 'en-US', languages: ['en-US'] };
  }
  
  return {
    primary: navigator.language || 'en-US',
    languages: navigator.languages ? Array.from(navigator.languages) : [navigator.language || 'en-US']
  };
}

/**
 * Detecta capacidades de hardware
 */
export function getHardwareInfo() {
  if (typeof navigator === 'undefined') {
    return {
      cpuCores: 4,
      deviceMemory: 4,
      maxTouchPoints: 0
    };
  }
  
  return {
    cpuCores: navigator.hardwareConcurrency || 4,
    deviceMemory: (navigator as any).deviceMemory || 4,
    maxTouchPoints: navigator.maxTouchPoints || 0
  };
}

/**
 * Detecta preferencias de accesibilidad
 */
export function getAccessibilityPreferences() {
  if (typeof window === 'undefined' || !window.matchMedia) {
    return {
      prefersContrast: false,
      prefersReducedMotion: false,
      prefersReducedTransparency: false
    };
  }
  
  return {
    prefersContrast: window.matchMedia('(prefers-contrast: high)').matches,
    prefersReducedMotion: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    prefersReducedTransparency: window.matchMedia('(prefers-reduced-transparency: reduce)').matches
  };
}

/**
 * Obtiene el nivel de zoom del navegador
 */
export function getZoomLevel(): number {
  if (typeof window === 'undefined') return 1.0;
  
  // Método 1: devicePixelRatio / (outerWidth / innerWidth)
  const outerZoom = window.outerWidth > 0 
    ? window.devicePixelRatio / (window.outerWidth / window.innerWidth)
    : 1.0;
  
  // Método 2: Basado en devicePixelRatio (más confiable)
  const dpr = window.devicePixelRatio || 1.0;
  
  // Si hay discrepancia grande, usar outerZoom, sino DPR
  if (Math.abs(outerZoom - dpr) > 0.5) {
    return parseFloat(outerZoom.toFixed(2));
  }
  
  return parseFloat(dpr.toFixed(2));
}

/**
 * Detecta si la app está instalada como PWA
 */
export function isPWA(): boolean {
  if (typeof window === 'undefined') return false;
  
  // Método 1: display-mode
  const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches;
  
  // Método 2: iOS standalone
  const isIOSStandalone = (window.navigator as any).standalone === true;
  
  return isStandaloneMode || isIOSStandalone;
}

/**
 * Obtiene la orientación de la pantalla
 */
export function getScreenOrientation(): string {
  if (typeof window === 'undefined' || !window.screen) return 'unknown';
  
  // API moderna
  if (window.screen.orientation) {
    return window.screen.orientation.type;
  }
  
  // Fallback basado en dimensiones
  const isPortrait = window.innerHeight > window.innerWidth;
  return isPortrait ? 'portrait-primary' : 'landscape-primary';
}

/**
 * Obtiene información de storage y privacidad
 */
export function getStorageInfo() {
  if (typeof navigator === 'undefined') {
    return {
      cookiesEnabled: false,
      doNotTrack: 'unspecified'
    };
  }
  
  return {
    cookiesEnabled: navigator.cookieEnabled,
    doNotTrack: (navigator as any).doNotTrack || (window as any).doNotTrack || 'unspecified'
  };
}

/**
 * Función helper para obtener toda la información del navegador de una vez
 */
export function getAllBrowserInfo() {
  return {
    browser: getBrowser(),
    os: getOS(),
    device: getDeviceType(),
    connection: getConnectionInfo(),
    timezone: getTimezone(),
    locale: getLocale(),
    hardware: getHardwareInfo(),
    accessibility: getAccessibilityPreferences(),
    zoom: getZoomLevel(),
    isPWA: isPWA(),
    orientation: getScreenOrientation(),
    storage: getStorageInfo(),
    isModern: isModernBrowser()
  };
}
