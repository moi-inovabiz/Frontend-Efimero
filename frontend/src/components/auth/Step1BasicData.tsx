/**
 * Step 1: Basic Data
 * - Email, password, nombre, apellido, RUT, teléfono
 * - Real-time RUT validation (módulo 11)
 * - Auto-detect tipo_cliente from RUT prefix
 */

'use client';

import { useState, useEffect } from 'react';
import { RegistrationData } from '@/lib/auth-client';

interface Step1Props {
  data: Partial<RegistrationData>;
  onUpdate: (data: Partial<RegistrationData>) => void;
  onNext: () => void;
}

export default function Step1BasicData({ data, onUpdate, onNext }: Step1Props) {
  const [email, setEmail] = useState(data.email || '');
  const [password, setPassword] = useState(data.password || '');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [nombre, setNombre] = useState(data.nombre || '');
  const [apellido, setApellido] = useState(data.apellido || '');
  const [rut, setRut] = useState(data.rut || '');
  const [telefono, setTelefono] = useState(data.telefono || '');
  
  const [rutError, setRutError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);
  
  const [rutValid, setRutValid] = useState(false);

  // RUT validation (Chilean módulo 11 algorithm)
  const validateRUT = (rutValue: string): boolean => {
    const cleaned = rutValue.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (cleaned.length < 2) return false;
    
    const body = cleaned.slice(0, -1);
    const checkDigit = cleaned.slice(-1);
    
    let sum = 0;
    let multiplier = 2;
    
    for (let i = body.length - 1; i >= 0; i--) {
      sum += parseInt(body[i]) * multiplier;
      multiplier = multiplier === 7 ? 2 : multiplier + 1;
    }
    
    const remainder = sum % 11;
    const expectedDigit = 11 - remainder;
    const expectedChar = expectedDigit === 11 ? '0' : expectedDigit === 10 ? 'K' : expectedDigit.toString();
    
    return checkDigit === expectedChar;
  };

  // Format RUT with hyphen (12345678-9)
  const formatRUT = (value: string): string => {
    const cleaned = value.replace(/[^0-9kK]/g, '').toUpperCase();
    
    if (cleaned.length <= 1) return cleaned;
    
    const body = cleaned.slice(0, -1);
    const checkDigit = cleaned.slice(-1);
    
    return `${body}-${checkDigit}`;
  };

  // Handle RUT input change
  const handleRutChange = (value: string) => {
    const cleaned = value.replace(/[^0-9kK-]/g, '').toUpperCase();
    setRut(cleaned);
    
    if (cleaned.length >= 3) {
      const isValid = validateRUT(cleaned);
      setRutValid(isValid);
      
      if (!isValid) {
        setRutError('RUT inválido');
      } else {
        setRutError(null);
        
        // Auto-detect tipo_cliente from RUT prefix
        const cleanedNoHyphen = cleaned.replace(/-/g, '');
        const prefix = cleanedNoHyphen.substring(0, 2);
        const tipoCliente = (prefix === '70' || prefix === '71' || prefix === '72' || 
                            prefix === '73' || prefix === '74' || prefix === '75' || 
                            prefix === '76' || prefix === '77' || prefix === '78' || 
                            prefix === '79' || prefix === '80' || prefix === '81' || 
                            prefix === '82' || prefix === '83' || prefix === '84' || 
                            prefix === '85' || prefix === '86' || prefix === '87' || 
                            prefix === '88' || prefix === '89')
          ? 'empresa'
          : 'persona';
        
        onUpdate({ tipo_cliente: tipoCliente });
      }
    } else {
      setRutError(null);
      setRutValid(false);
    }
  };

  // Validate email format
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Validate password strength
  const validatePassword = (password: string): boolean => {
    return (
      password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /[0-9]/.test(password)
    );
  };

  // Handle email blur
  const handleEmailBlur = () => {
    if (email && !validateEmail(email)) {
      setEmailError('Formato de email inválido');
    } else {
      setEmailError(null);
    }
  };

  // Handle password blur
  const handlePasswordBlur = () => {
    if (password && !validatePassword(password)) {
      setPasswordError('La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas y números');
    } else if (confirmPassword && password !== confirmPassword) {
      setPasswordError('Las contraseñas no coinciden');
    } else {
      setPasswordError(null);
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields
    if (!email || !validateEmail(email)) {
      setEmailError('Email inválido');
      return;
    }
    
    if (!password || !validatePassword(password)) {
      setPasswordError('Contraseña no cumple requisitos mínimos');
      return;
    }
    
    if (password !== confirmPassword) {
      setPasswordError('Las contraseñas no coinciden');
      return;
    }
    
    if (!rut || !rutValid) {
      setRutError('RUT inválido o incompleto');
      return;
    }
    
    if (!nombre || !apellido) {
      return;
    }
    
    // Format RUT before saving
    const formattedRut = formatRUT(rut);
    
    // Update parent data
    onUpdate({
      email,
      password,
      nombre,
      apellido,
      rut: formattedRut,
      telefono: telefono || undefined,
    });
    
    // Go to next step
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Nombre */}
        <div>
          <label htmlFor="nombre" className="block text-sm font-medium text-gray-300 mb-2">
            Nombre *
          </label>
          <input
            type="text"
            id="nombre"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
            required
          />
        </div>

        {/* Apellido */}
        <div>
          <label htmlFor="apellido" className="block text-sm font-medium text-gray-300 mb-2">
            Apellido *
          </label>
          <input
            type="text"
            id="apellido"
            value={apellido}
            onChange={(e) => setApellido(e.target.value)}
            className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
            required
          />
        </div>
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
          Email *
        </label>
        <input
          type="email"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={handleEmailBlur}
          className={`w-full px-4 py-3 bg-gray-700/50 border ${
            emailError ? 'border-red-500' : 'border-gray-600'
          } rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white`}
          required
        />
        {emailError && <p className="text-red-400 text-sm mt-1">{emailError}</p>}
      </div>

      {/* RUT */}
      <div>
        <label htmlFor="rut" className="block text-sm font-medium text-gray-300 mb-2">
          RUT * <span className="text-gray-500 text-xs">(formato: 12345678-9)</span>
        </label>
        <input
          type="text"
          id="rut"
          value={rut}
          onChange={(e) => handleRutChange(e.target.value)}
          placeholder="12345678-9"
          className={`w-full px-4 py-3 bg-gray-700/50 border ${
            rutError ? 'border-red-500' : rutValid ? 'border-green-500' : 'border-gray-600'
          } rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white`}
          required
        />
        {rutError && <p className="text-red-400 text-sm mt-1">{rutError}</p>}
        {rutValid && !rutError && (
          <p className="text-green-400 text-sm mt-1 flex items-center">
            <span className="mr-1">✓</span> RUT válido
          </p>
        )}
      </div>

      {/* Teléfono */}
      <div>
        <label htmlFor="telefono" className="block text-sm font-medium text-gray-300 mb-2">
          Teléfono <span className="text-gray-500 text-xs">(opcional)</span>
        </label>
        <input
          type="tel"
          id="telefono"
          value={telefono}
          onChange={(e) => setTelefono(e.target.value)}
          placeholder="+569 1234 5678"
          className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
        />
      </div>

      {/* Password */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
          Contraseña *
        </label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={handlePasswordBlur}
          className={`w-full px-4 py-3 bg-gray-700/50 border ${
            passwordError ? 'border-red-500' : 'border-gray-600'
          } rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white`}
          required
        />
        <p className="text-gray-500 text-xs mt-1">
          Mínimo 8 caracteres, incluir mayúsculas, minúsculas y números
        </p>
      </div>

      {/* Confirm Password */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
          Confirmar Contraseña *
        </label>
        <input
          type="password"
          id="confirmPassword"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          onBlur={handlePasswordBlur}
          className={`w-full px-4 py-3 bg-gray-700/50 border ${
            passwordError ? 'border-red-500' : 'border-gray-600'
          } rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white`}
          required
        />
        {passwordError && <p className="text-red-400 text-sm mt-1">{passwordError}</p>}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all transform hover:scale-[1.02]"
      >
        Continuar →
      </button>
    </form>
  );
}
