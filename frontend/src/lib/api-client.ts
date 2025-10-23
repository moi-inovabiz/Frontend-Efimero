/**
 * Cliente API para comunicación con FastAPI
 * Maneja las solicitudes de FASE 2 y feedback de FASE 3
 */

import { AdaptiveUIRequest, AdaptiveUIResponse, BehaviorFeedback } from '@/types/adaptive-ui';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class AdaptiveUIClient {
  
  /**
   * FASE 2: Solicita predicción adaptativa al backend
   */
  static async requestAdaptiveDesign(request: AdaptiveUIRequest): Promise<AdaptiveUIResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/adaptive-ui/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Incluir JWT si existe
          ...(this.getAuthToken() && { 'Authorization': `Bearer ${this.getAuthToken()}` })
        },
        credentials: 'include', // Para cookies de primera parte
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Error solicitando diseño adaptativo:', error);
      throw error;
    }
  }

  /**
   * FASE 3: Envía feedback de comportamiento
   */
  static async sendFeedback(feedback: BehaviorFeedback): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/adaptive-ui/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.getAuthToken() && { 'Authorization': `Bearer ${this.getAuthToken()}` })
        },
        credentials: 'include',
        body: JSON.stringify(feedback)
      });

      if (!response.ok) {
        console.warn(`⚠️ Error enviando feedback: ${response.status}`);
      }
    } catch (error) {
      console.warn('⚠️ Error enviando feedback:', error);
      // No lanzar error para no interrumpir la UX
    }
  }

  /**
   * Obtiene token JWT del localStorage
   */
  private static getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  /**
   * Establece token JWT en localStorage
   */
  static setAuthToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  /**
   * Remueve token JWT
   */
  static removeAuthToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Obtiene o crea user_temp_id para usuarios anónimos
   */
  static getUserTempId(): string {
    if (typeof window !== 'undefined') {
      let tempId = localStorage.getItem('user_temp_id');
      if (!tempId) {
        tempId = `anon_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('user_temp_id', tempId);
      }
      return tempId;
    }
    return '';
  }
}