/**
 * Tipos TypeScript para el Frontend Efímero
 * Definiciones compartidas entre frontend y backend
 */

export interface DesignTokens {
  css_classes: string[];
  css_variables: Record<string, string>;
}

export interface AdaptiveUIResponse {
  design_tokens: DesignTokens;
  prediction_confidence: {
    classification: number;
    regression: number;
  };
  processing_time_ms: number;
}

export interface UserContext {
  hora_local: string;
  prefers_color_scheme: 'light' | 'dark' | 'no-preference';
  viewport_width: number;
  viewport_height: number;
  touch_enabled: boolean;
  device_pixel_ratio: number;
  user_agent: string;
  referer?: string;
  session_id: string;
  page_path: string;
}

export interface AdaptiveUIRequest {
  user_context: UserContext;
  user_temp_id?: string;
}

export interface BehaviorFeedback {
  action_type: 'click' | 'scroll' | 'hover' | 'focus' | 'error';
  element_id?: string;
  element_class?: string;
  timestamp: string;
  session_duration?: number;
  performance_metrics?: Record<string, any>;
}