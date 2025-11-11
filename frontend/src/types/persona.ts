/**
 * Tipos TypeScript para Personas Simuladas
 */

export interface PersonaSimulada {
  id: string;
  nombre: string;
  apellido: string;
  edad: number;
  fecha_nacimiento: string | null;
  region: string;
  tipo_cliente: 'persona' | 'empresa';
  interes_principal: string | null;
  uso_previsto: string | null;
  presupuesto: string | null;
  tiene_vehiculo_actual: boolean;
  tamano_flota: number | null;
  esquema_colores: string | null;
  color_favorito: string | null;
  estilo_tipografia: string | null;
  densidad_informacion: string | null;
  nivel_animaciones: string | null;
  preferencia_layout: string | null;
  estilo_navegacion: string | null;
  descripcion: string | null;
}

export interface AssignmentInfo {
  assigned_at: string;
  last_seen_at: string;
  page_views: number;
}

export interface PersonaAssignmentResponse {
  success: boolean;
  persona: PersonaSimulada;
  session_id: string;
  is_new_assignment: boolean;
  assignment_info: AssignmentInfo;
  message?: string;
  matching_score?: number; // Score del matching inteligente (0-100)
  matching_info?: {
    used_context: boolean;
    context_fields?: {
      hora: number;
      region: string;
      dispositivo: string;
      fin_semana: boolean;
    };
    note?: string;
  };
}

export interface PersonaMeResponse {
  success: boolean;
  persona: PersonaSimulada;
  session_id: string;
  assignment_info: AssignmentInfo;
}
