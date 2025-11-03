/**
 * Behavior Tracker
 * Recolecta métricas de comportamiento del usuario en tiempo real
 * Para mejorar las predicciones del sistema adaptativo
 */

export interface BehaviorMetrics {
  idle_time_seconds: number;
  avg_scroll_speed: number;
  avg_typing_speed: number;
  error_rate: number;
  prefers_keyboard: boolean;
  max_scroll_depth: number;
  total_interactions: number;
  session_duration_seconds: number;
}

export class BehaviorTracker {
  private lastActivity: number;
  private scrollSpeeds: number[];
  private typingIntervals: number[];
  private totalClicks: number;
  private clickMisses: number;
  private keyboardActions: number;
  private mouseActions: number;
  private maxScrollDepth: number;
  private totalInteractions: number;
  private sessionStart: number;
  private isTracking: boolean;
  
  // Configuración
  private readonly MAX_SAMPLES = 50;
  private readonly IDLE_CHECK_INTERVAL = 5000; // 5 segundos
  
  constructor() {
    this.lastActivity = Date.now();
    this.scrollSpeeds = [];
    this.typingIntervals = [];
    this.totalClicks = 0;
    this.clickMisses = 0;
    this.keyboardActions = 0;
    this.mouseActions = 0;
    this.maxScrollDepth = 0;
    this.totalInteractions = 0;
    this.sessionStart = Date.now();
    this.isTracking = false;
  }
  
  /**
   * Inicia el tracking de comportamiento
   */
  public startTracking(): void {
    if (this.isTracking) return;
    
    this.isTracking = true;
    this.sessionStart = Date.now();
    
    // Track idle time
    this.trackIdleTime();
    
    // Track scroll behavior
    this.trackScrollBehavior();
    
    // Track typing speed
    this.trackTypingSpeed();
    
    // Track error rate (clicks fallidos)
    this.trackErrorRate();
    
    // Track input preference
    this.trackInputPreference();
    
    // Track scroll depth
    this.trackScrollDepth();
    
    console.log('🎯 BehaviorTracker: Tracking iniciado');
  }
  
  /**
   * Detiene el tracking de comportamiento
   */
  public stopTracking(): void {
    this.isTracking = false;
    console.log('🎯 BehaviorTracker: Tracking detenido');
  }
  
  /**
   * Obtiene las métricas actuales
   */
  public getMetrics(): BehaviorMetrics {
    return {
      idle_time_seconds: this.getIdleTimeSeconds(),
      avg_scroll_speed: this.getAvgScrollSpeed(),
      avg_typing_speed: this.getAvgTypingSpeed(),
      error_rate: this.getErrorRate(),
      prefers_keyboard: this.getPrefersKeyboard(),
      max_scroll_depth: this.getMaxScrollDepth(),
      total_interactions: this.totalInteractions,
      session_duration_seconds: this.getSessionDurationSeconds()
    };
  }
  
  /**
   * Resetea todas las métricas
   */
  public reset(): void {
    this.lastActivity = Date.now();
    this.scrollSpeeds = [];
    this.typingIntervals = [];
    this.totalClicks = 0;
    this.clickMisses = 0;
    this.keyboardActions = 0;
    this.mouseActions = 0;
    this.maxScrollDepth = 0;
    this.totalInteractions = 0;
    this.sessionStart = Date.now();
  }
  
  // ========== TRACKING METHODS ==========
  
  private trackIdleTime(): void {
    if (typeof globalThis.window === 'undefined') return;
    
    const updateActivity = () => {
      this.lastActivity = Date.now();
    };
    
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    for (const event of events) {
      document.addEventListener(event, updateActivity, { passive: true });
    }
  }
  
  private trackScrollBehavior(): void {
    if (typeof globalThis.window === 'undefined') return;
    
    let lastScrollY = window.scrollY;
    let lastScrollTime = Date.now();
    
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const currentTime = Date.now();
      
      const scrollDelta = Math.abs(currentScrollY - lastScrollY);
      const timeDelta = currentTime - lastScrollTime;
      
      if (timeDelta > 0) {
        const speed = scrollDelta / timeDelta; // pixels por ms
        
        this.scrollSpeeds.push(speed);
        if (this.scrollSpeeds.length > this.MAX_SAMPLES) {
          this.scrollSpeeds.shift();
        }
      }
      
      lastScrollY = currentScrollY;
      lastScrollTime = currentTime;
      
      this.totalInteractions++;
    };
    
    let scrollTimeout: NodeJS.Timeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(handleScroll, 100);
    }, { passive: true });
  }
  
  private trackTypingSpeed(): void {
    if (typeof globalThis.window === 'undefined') return;
    
    let lastKeyTime = Date.now();
    
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignorar teclas especiales
      if (e.key.length > 1 && !['Backspace', 'Enter', 'Space'].includes(e.key)) {
        return;
      }
      
      const currentTime = Date.now();
      const interval = currentTime - lastKeyTime;
      
      // Solo registrar si el intervalo es razonable (50ms - 2000ms)
      if (interval >= 50 && interval <= 2000) {
        this.typingIntervals.push(interval);
        if (this.typingIntervals.length > this.MAX_SAMPLES) {
          this.typingIntervals.shift();
        }
      }
      
      lastKeyTime = currentTime;
      this.totalInteractions++;
    };
    
    document.addEventListener('keydown', handleKeyDown, { passive: true });
  }
  
  private trackErrorRate(): void {
    if (typeof globalThis.window === 'undefined') return;
    
    const handleClick = (e: MouseEvent) => {
      this.totalClicks++;
      
      // Si el click fue en el body o html (sin target específico), considerarlo "miss"
      const target = e.target as HTMLElement;
      if (target === document.body || target === document.documentElement) {
        this.clickMisses++;
      }
      
      // También considerar miss si el target no tiene ninguna acción asociada
      if (target && !target.onclick && !target.closest('a, button, input, select, textarea, [role="button"]')) {
        this.clickMisses++;
      }
      
      this.totalInteractions++;
    };
    
    document.addEventListener('click', handleClick, { passive: true });
  }
  
  private trackInputPreference(): void {
    if (typeof globalThis.window === 'undefined') return;
    
    document.addEventListener('keydown', () => {
      this.keyboardActions++;
    }, { passive: true });
    
    document.addEventListener('click', () => {
      this.mouseActions++;
    }, { passive: true });
    
    document.addEventListener('touchstart', () => {
      this.mouseActions++; // Touch se considera como mouse para esta métrica
    }, { passive: true });
  }
  
  private trackScrollDepth(): void {
    if (typeof globalThis.window === 'undefined') return;
    
    const updateScrollDepth = () => {
      const scrolled = window.scrollY + window.innerHeight;
      const total = document.documentElement.scrollHeight;
      
      if (total > 0) {
        const depth = (scrolled / total) * 100;
        this.maxScrollDepth = Math.max(this.maxScrollDepth, Math.min(100, depth));
      }
    };
    
    let scrollDepthTimeout: NodeJS.Timeout;
    window.addEventListener('scroll', () => {
      clearTimeout(scrollDepthTimeout);
      scrollDepthTimeout = setTimeout(updateScrollDepth, 200);
    }, { passive: true });
  }
  
  // ========== GETTER METHODS ==========
  
  private getIdleTimeSeconds(): number {
    return Math.floor((Date.now() - this.lastActivity) / 1000);
  }
  
  private getAvgScrollSpeed(): number {
    if (this.scrollSpeeds.length === 0) return 0;
    
    const sum = this.scrollSpeeds.reduce((acc, speed) => acc + speed, 0);
    return Number.parseFloat((sum / this.scrollSpeeds.length).toFixed(4));
  }
  
  private getAvgTypingSpeed(): number {
    if (this.typingIntervals.length === 0) return 0;
    
    // Calcular WPM (words per minute)
    // Asumiendo 5 caracteres = 1 palabra
    const avgInterval = this.typingIntervals.reduce((acc, interval) => acc + interval, 0) / this.typingIntervals.length;
    
    if (avgInterval === 0) return 0;
    
    const charsPerMinute = 60000 / avgInterval;
    const wpm = charsPerMinute / 5;
    
    return Number.parseFloat(wpm.toFixed(2));
  }
  
  private getErrorRate(): number {
    if (this.totalClicks === 0) return 0;
    
    return Number.parseFloat((this.clickMisses / this.totalClicks).toFixed(4));
  }
  
  private getPrefersKeyboard(): boolean {
    // Si hay actividad significativa
    const totalActions = this.keyboardActions + this.mouseActions;
    if (totalActions < 10) return false;
    
    // Si más del 60% son acciones de teclado
    return (this.keyboardActions / totalActions) > 0.6;
  }
  
  private getMaxScrollDepth(): number {
    return Number.parseFloat(this.maxScrollDepth.toFixed(2));
  }
  
  private getSessionDurationSeconds(): number {
    return Math.floor((Date.now() - this.sessionStart) / 1000);
  }
}

// Instancia global singleton
let globalTracker: BehaviorTracker | null = null;

/**
 * Obtiene o crea la instancia global del BehaviorTracker
 */
export function getBehaviorTracker(): BehaviorTracker {
  globalTracker ??= new BehaviorTracker();
  return globalTracker;
}

/**
 * Inicia el tracking global de comportamiento
 */
export function startBehaviorTracking(): void {
  const tracker = getBehaviorTracker();
  tracker.startTracking();
}

/**
 * Detiene el tracking global de comportamiento
 */
export function stopBehaviorTracking(): void {
  if (globalTracker) {
    globalTracker.stopTracking();
  }
}

/**
 * Obtiene las métricas globales de comportamiento
 */
export function getBehaviorMetrics(): BehaviorMetrics {
  const tracker = getBehaviorTracker();
  return tracker.getMetrics();
}
