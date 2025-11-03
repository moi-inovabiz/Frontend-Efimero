/**
 * Step 2: Automotive Profile
 * - tipo_cliente (auto-detected from RUT, read-only)
 * - region (Chile regions dropdown)
 * - interes_principal (multi-select: autos lujo, SUVs, camiones, etc.)
 * - uso_previsto (personal, ejecutivo, transporte, minería, etc.)
 * - presupuesto (slider)
 * - tiene_vehiculo_actual (toggle)
 * - fecha_nacimiento (if persona) OR tamano_flota (if empresa)
 */

'use client';

import { useState } from 'react';
import { RegistrationData } from '@/lib/auth-client';

interface Step2Props {
  data: Partial<RegistrationData>;
  onUpdate: (data: Partial<RegistrationData>) => void;
  onNext: () => void;
  onBack: () => void;
}

const REGIONES_CHILE = [
  'Región de Arica y Parinacota',
  'Región de Tarapacá',
  'Región de Antofagasta',
  'Región de Atacama',
  'Región de Coquimbo',
  'Región de Valparaíso',
  'Región Metropolitana',
  'Región del Libertador General Bernardo O\'Higgins',
  'Región del Maule',
  'Región de Ñuble',
  'Región del Biobío',
  'Región de La Araucanía',
  'Región de Los Ríos',
  'Región de Los Lagos',
  'Región de Aysén del General Carlos Ibáñez del Campo',
  'Región de Magallanes y de la Antártica Chilena',
];

const INTERESES = [
  { value: 'autos_lujo', label: 'Autos de Lujo' },
  { value: 'suvs', label: 'SUVs y Crossovers' },
  { value: 'vans', label: 'Vans y Monovolúmenes' },
  { value: 'camiones_livianos', label: 'Camiones Livianos' },
  { value: 'camiones_pesados', label: 'Camiones Pesados' },
  { value: 'buses', label: 'Buses' },
  { value: 'electricos', label: 'Vehículos Eléctricos' },
];

const USOS_PREVISTOS = [
  { value: 'personal', label: 'Uso Personal' },
  { value: 'ejecutivo', label: 'Ejecutivo/Corporativo' },
  { value: 'transporte', label: 'Transporte de Carga' },
  { value: 'mineria', label: 'Minería' },
  { value: 'construccion', label: 'Construcción' },
  { value: 'agricola', label: 'Agrícola' },
];

const PRESUPUESTO_RANGES = [
  { value: 'menos_30m', label: 'Menos de $30M', min: 0, max: 30 },
  { value: '30m_60m', label: '$30M - $60M', min: 30, max: 60 },
  { value: '60m_100m', label: '$60M - $100M', min: 60, max: 100 },
  { value: '100m_150m', label: '$100M - $150M', min: 100, max: 150 },
  { value: 'mas_150m', label: 'Más de $150M', min: 150, max: 200 },
];

export default function Step2Profile({ data, onUpdate, onNext, onBack }: Step2Props) {
  const [region, setRegion] = useState(data.region || '');
  const [intereses, setIntereses] = useState<string[]>(data.interes_principal || []);
  const [uso, setUso] = useState(data.uso_previsto || '');
  const [presupuesto, setPresupuesto] = useState(data.presupuesto || 'menos_30m');
  const [tieneVehiculo, setTieneVehiculo] = useState(data.tiene_vehiculo_actual || false);
  const [fechaNacimiento, setFechaNacimiento] = useState(data.fecha_nacimiento || '');
  const [tamanoFlota, setTamanoFlota] = useState(data.tamano_flota?.toString() || '');

  const isEmpresa = data.tipo_cliente === 'empresa';
  const tipoClienteLabel = isEmpresa ? 'Empresa' : 'Persona Natural';

  // Handle intereses toggle
  const toggleInteres = (value: string) => {
    setIntereses((prev) =>
      prev.includes(value) ? prev.filter((i) => i !== value) : [...prev, value]
    );
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate required fields
    if (!region || intereses.length === 0 || !uso || !presupuesto) {
      return;
    }

    if (!isEmpresa && !fechaNacimiento) {
      return;
    }

    if (isEmpresa && !tamanoFlota) {
      return;
    }

    // Update parent data
    const updateData: Partial<RegistrationData> = {
      region,
      interes_principal: intereses,
      uso_previsto: uso,
      presupuesto,
      tiene_vehiculo_actual: tieneVehiculo,
    };

    if (!isEmpresa) {
      updateData.fecha_nacimiento = fechaNacimiento;
    } else {
      updateData.tamano_flota = Number.parseInt(tamanoFlota);
    }

    onUpdate(updateData);
    onNext();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Tipo Cliente (read-only) */}
      <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-400">Tipo de Cliente</p>
            <p className="text-lg font-semibold text-cyan-400">{tipoClienteLabel}</p>
          </div>
          <div className="text-3xl">{isEmpresa ? '🏢' : '👤'}</div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Detectado automáticamente desde tu RUT
        </p>
      </div>

      {/* Fecha Nacimiento (persona) OR Tamaño Flota (empresa) */}
      {!isEmpresa ? (
        <div>
          <label htmlFor="fechaNacimiento" className="block text-sm font-medium text-gray-300 mb-2">
            Fecha de Nacimiento *
          </label>
          <input
            type="date"
            id="fechaNacimiento"
            value={fechaNacimiento}
            onChange={(e) => setFechaNacimiento(e.target.value)}
            max={new Date().toISOString().split('T')[0]}
            className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
            required
          />
        </div>
      ) : (
        <div>
          <label htmlFor="tamanoFlota" className="block text-sm font-medium text-gray-300 mb-2">
            Tamaño de Flota * <span className="text-gray-500 text-xs">(cantidad de vehículos)</span>
          </label>
          <input
            type="number"
            id="tamanoFlota"
            value={tamanoFlota}
            onChange={(e) => setTamanoFlota(e.target.value)}
            min="1"
            max="10000"
            placeholder="Ej: 50"
            className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
            required
          />
        </div>
      )}

      {/* Región */}
      <div>
        <label htmlFor="region" className="block text-sm font-medium text-gray-300 mb-2">
          Región *
        </label>
        <select
          id="region"
          value={region}
          onChange={(e) => setRegion(e.target.value)}
          className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
          required
        >
          <option value="">Selecciona tu región</option>
          {REGIONES_CHILE.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {/* Intereses Principales */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Intereses Principales * <span className="text-gray-500 text-xs">(selecciona al menos uno)</span>
        </label>
        <div className="grid grid-cols-2 gap-3">
          {INTERESES.map((interes) => (
            <button
              key={interes.value}
              type="button"
              onClick={() => toggleInteres(interes.value)}
              className={`p-4 rounded-lg border-2 transition-all text-left ${
                intereses.includes(interes.value)
                  ? 'border-cyan-500 bg-cyan-500/10 text-cyan-300'
                  : 'border-gray-600 bg-gray-700/30 text-gray-400 hover:border-gray-500'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{interes.label}</span>
                {intereses.includes(interes.value) && (
                  <span className="text-cyan-400">✓</span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Uso Previsto */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-3">
          Uso Previsto *
        </label>
        <div className="space-y-2">
          {USOS_PREVISTOS.map((usoItem) => (
            <label
              key={usoItem.value}
              className={`flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                uso === usoItem.value
                  ? 'border-cyan-500 bg-cyan-500/10'
                  : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
              }`}
            >
              <input
                type="radio"
                name="uso"
                value={usoItem.value}
                checked={uso === usoItem.value}
                onChange={(e) => setUso(e.target.value)}
                className="w-4 h-4 text-cyan-500 border-gray-600 focus:ring-cyan-500 focus:ring-offset-gray-800"
                required
              />
              <span className={`ml-3 font-medium ${uso === usoItem.value ? 'text-cyan-300' : 'text-gray-400'}`}>
                {usoItem.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Presupuesto */}
      <div>
        <label htmlFor="presupuesto" className="block text-sm font-medium text-gray-300 mb-2">
          Rango de Presupuesto *
        </label>
        <select
          id="presupuesto"
          value={presupuesto}
          onChange={(e) => setPresupuesto(e.target.value)}
          className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-white"
          required
        >
          {PRESUPUESTO_RANGES.map((range) => (
            <option key={range.value} value={range.value}>
              {range.label}
            </option>
          ))}
        </select>
      </div>

      {/* Tiene Vehículo Actual */}
      <div className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg border border-gray-600">
        <div>
          <p className="font-medium text-gray-300">¿Tienes vehículo actualmente?</p>
          <p className="text-sm text-gray-500">Esto nos ayuda a evaluar trade-in</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={tieneVehiculo}
            onChange={(e) => setTieneVehiculo(e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-cyan-500/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
        </label>
      </div>

      {/* Navigation Buttons */}
      <div className="flex gap-4">
        <button
          type="button"
          onClick={onBack}
          className="flex-1 bg-gray-700 text-gray-300 py-3 rounded-lg font-semibold hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all"
        >
          ← Atrás
        </button>
        <button
          type="submit"
          className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 focus:ring-offset-gray-800 transition-all transform hover:scale-[1.02]"
        >
          Continuar →
        </button>
      </div>
    </form>
  );
}
