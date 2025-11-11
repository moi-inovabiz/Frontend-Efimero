/**
 * Registration Wizard - 3 Steps
 * Step 1: Basic Data (email, password, RUT, nombre)
 * Step 2: Profile (tipo_cliente, región, intereses, presupuesto)
 * Step 3: Visual Preferences (colores, tipografía, densidad) - OPCIONAL
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { RegistrationData } from '@/lib/auth-client';
import Step1BasicData from '@/components/auth/Step1BasicData';
import Step2Profile from '@/components/auth/Step2Profile';
import Step3VisualPreferences from '@/components/auth/Step3VisualPreferences';
import { PersonaDebugPanel } from '@/components/persona/PersonaDebugPanel';
import { AdaptiveUIProvider } from '@/components/adaptive/AdaptiveUIProvider';

export default function RegisterPage() {
  const router = useRouter();
  const { register, error: authError, clearError } = useAuth();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Form data state
  const [formData, setFormData] = useState<Partial<RegistrationData>>({
    tiene_vehiculo_actual: false,
    visual_preferences: {
      esquema_colores: 'automatico',
      color_favorito: 'azul',
      estilo_tipografia: 'moderna_geometrica',
      densidad_informacion: 'comoda',
      nivel_animaciones: 'moderadas',
    },
  });

  const totalSteps = 3;

  const handleNext = () => {
    setCurrentStep((prev) => Math.min(prev + 1, totalSteps));
  };

  const handleBack = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleUpdateData = (stepData: Partial<RegistrationData>) => {
    setFormData((prev) => ({
      ...prev,
      ...stepData,
    }));
  };

  const handleSkipVisualPreferences = async () => {
    await handleSubmit(true);
  };

  const handleSubmit = async (skipVisualPrefs = false) => {
    setLoading(true);
    setError(null);
    clearError();

    try {
      const dataToSubmit = skipVisualPrefs
        ? { ...formData, visual_preferences: undefined }
        : formData;

      await register(dataToSubmit as RegistrationData);
      // Redirect to loading page to prepare SSR and apply theme
      router.push('/loading-dashboard');
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Error al registrarse';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AdaptiveUIProvider>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-black p-4">
        {/* Persona Debug Panel */}
        <PersonaDebugPanel position="top-right" collapsed={true} />
        
        <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
            Crear Cuenta
          </h1>
          <p className="text-gray-400">
            Completa los siguientes pasos para personalizar tu experiencia
          </p>
        </div>

        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between max-w-2xl mx-auto">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center flex-1">
                <div className="flex items-center flex-col">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${
                      step < currentStep
                        ? 'bg-green-500 text-white'
                        : step === currentStep
                        ? 'bg-cyan-500 text-white ring-4 ring-cyan-500/30'
                        : 'bg-gray-700 text-gray-400'
                    }`}
                  >
                    {step < currentStep ? '✓' : step}
                  </div>
                  <span className="text-xs text-gray-400 mt-2">
                    {step === 1 ? 'Datos Básicos' : step === 2 ? 'Perfil' : 'Preferencias'}
                  </span>
                </div>
                {step < totalSteps && (
                  <div
                    className={`h-1 flex-1 mx-2 transition-all ${
                      step < currentStep ? 'bg-green-500' : 'bg-gray-700'
                    }`}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 shadow-2xl">
          {/* Error Message */}
          {(error || authError) && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 mb-6">
              <p className="text-red-400 text-sm">
                {error || authError}
              </p>
            </div>
          )}

          {/* Step Content */}
          {currentStep === 1 && (
            <Step1BasicData
              data={formData}
              onUpdate={handleUpdateData}
              onNext={handleNext}
            />
          )}

          {currentStep === 2 && (
            <Step2Profile
              data={formData}
              onUpdate={handleUpdateData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}

          {currentStep === 3 && (
            <Step3VisualPreferences
              data={formData}
              onUpdate={handleUpdateData}
              onSubmit={() => handleSubmit(false)}
              onSkip={handleSkipVisualPreferences}
              onBack={handleBack}
              loading={loading}
            />
          )}
        </div>

        {/* Login Link */}
        {currentStep === 1 && (
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              ¿Ya tienes cuenta?{' '}
              <Link 
                href="/login" 
                className="text-cyan-400 hover:text-cyan-300 font-semibold transition-colors"
              >
                Inicia sesión aquí
              </Link>
            </p>
          </div>
        )}

        {/* Back to Home */}
        <div className="mt-4 text-center">
          <Link 
            href="/" 
            className="inline-flex items-center gap-2 text-gray-400 hover:text-cyan-400 text-sm transition-colors font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Volver al inicio
          </Link>
        </div>
      </div>
    </div>
    </AdaptiveUIProvider>
  );
}
