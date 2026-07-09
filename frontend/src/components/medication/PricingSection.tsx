import { useState } from 'react';
import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import type { PricingData } from '../../types/medication';
import { PRICING } from '../../constants/copy';

interface PricingSectionProps { pricing: PricingData; }

function formatCOP(n: number): string {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n);
}

export default function PricingSection({ pricing }: PricingSectionProps) {
  const { averageMarketPrice, maxRegulatedPrice, currency, priceHistory, referencePrices } = pricing;
  const [showInfo, setShowInfo] = useState(false);

  // Solo el 30% del catálogo tiene techo regulado (Circular CNPMDM); sin él no hay comparación
  const hayTecho  = maxRegulatedPrice > 0;

  // Punto vigente al final de la serie: mediana de la referencia Clicsalud (oct-2024),
  // marcado como serie aparte para que la línea de tiempo no termine en 2019
  const preciosRef = (referencePrices ?? []).map((r) => r.precio).sort((a, b) => a - b);
  const medianaRef = preciosRef.length
    ? preciosRef[Math.floor(preciosRef.length / 2)]
    : null;
  const datosGrafica = medianaRef !== null && priceHistory.length > 0
    ? [...priceHistory, { period: 'ref. oct 2024', referencia: medianaRef } as never]
    : priceHistory;
  const pctOfMax  = hayTecho ? Math.round((averageMarketPrice / maxRegulatedPrice) * 100) : null;
  const aboveMax  = hayTecho && averageMarketPrice > maxRegulatedPrice;

  const cards = [
    {
      id: 'avg',
      label: PRICING.averageLabel,
      value: averageMarketPrice > 0 ? formatCOP(averageMarketPrice) : PRICING.noDataLabel,
      meta:  averageMarketPrice > 0 ? currency : 'Sin reportes en SISMED 2017–2019',
      color: aboveMax ? 'text-high' : 'text-primary',
      bg:    aboveMax ? 'bg-high-bg border-high' : 'bg-primary-bg border-primary',
      icon:  '💰',
    },
    {
      id: 'max',
      label: PRICING.regulatedLabel,
      value: hayTecho ? formatCOP(maxRegulatedPrice) : PRICING.notRegulatedValue,
      meta:  hayTecho ? PRICING.sourceLabel : PRICING.notRegulatedMeta,
      color: 'text-slate-900',
      bg:    'bg-slate-50 border-slate-200',
      icon:  '🏛️',
    },
    hayTecho
      ? {
          id: 'pct',
          label: `${pctOfMax}% del máximo`,
          value: `${pctOfMax}%`,
          meta:  aboveMax ? 'Por encima del límite' : 'Dentro del límite',
          color: aboveMax ? 'text-high' : 'text-low',
          bg:    aboveMax ? 'bg-high-bg border-high' : 'bg-low-bg border-low',
          icon:  aboveMax ? '⚠️' : '✅',
        }
      : {
          id: 'pct',
          label: 'Comparación con el techo',
          value: '—',
          meta:  'Sin techo regulado no hay límite contra el cual comparar',
          color: 'text-slate-400',
          bg:    'bg-slate-50 border-slate-200',
          icon:  'ℹ️',
        },
  ];

  return (
    <section
      className="bg-white border border-slate-200 rounded-2xl shadow-card overflow-hidden"
      aria-labelledby="pricing-section-title"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span className="text-[22px]" aria-hidden="true">💹</span>
          <h2 id="pricing-section-title" className="text-lg font-bold text-slate-900 tracking-[-0.02em]">
            {PRICING.sectionTitle}
          </h2>
        </div>
        <button
          className="text-xs font-semibold text-primary bg-primary-bg px-3 py-1.5 rounded-full border border-primary/20 transition-colors hover:bg-primary hover:text-white cursor-pointer"
          onClick={() => setShowInfo(p => !p)}
          aria-expanded={showInfo}
          aria-controls="pricing-edu-panel"
        >
          {showInfo ? '✕ Cerrar' : '¿Qué es esto?'}
        </button>
      </div>

      {/* Collapsible education panel */}
      {showInfo && (
        <div
          id="pricing-edu-panel"
          className="mx-6 mt-4 bg-primary-bg border border-primary/15 border-l-4 border-l-primary rounded-lg p-4 text-sm text-slate-500 leading-[1.7] animate-[fade-in_0.25s_ease]"
          role="region"
          aria-label="De dónde vienen los precios"
        >
          {PRICING.educationBody}
        </div>
      )}

      <div className="p-6 flex flex-col gap-6">
        {/* Price cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {cards.map(card => (
            <div
              key={card.id}
              className={`p-4 rounded-lg border ${card.bg} flex flex-col gap-1`}
              aria-label={`${card.label}: ${card.value}`}
            >
              <div className="flex items-center gap-2 text-base" aria-hidden="true">{card.icon}</div>
              <span className="text-xs font-semibold tracking-wider uppercase text-slate-400 leading-none">
                {card.label}
              </span>
              <span className={`text-xl font-bold tracking-[-0.03em] ${card.color}`}>{card.value}</span>
              <span className="text-xs text-slate-400">{card.meta}</span>
            </div>
          ))}
        </div>

        {/* Precio de referencia vigente por unidad (Clicsalud oct-2024) */}
        {referencePrices && referencePrices.length > 0 && (
          <div>
            <p className="text-xs font-semibold tracking-[0.06em] uppercase text-slate-400 mb-3">
              {PRICING.referenceTitle}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {['Comercial', 'Institucional'].map((canal) => {
                const delCanal = referencePrices.filter((r) => r.canal === canal);
                if (delCanal.length === 0) return null;
                const precios = delCanal.map((r) => r.precio);
                const min = Math.min(...precios);
                const max = Math.max(...precios);
                const unidad = delCanal[0].unidad ?? 'unidad';
                return (
                  <div key={canal} className="p-4 rounded-lg border bg-slate-50 border-slate-200 flex flex-col gap-1">
                    <span className="text-xs font-semibold tracking-wider uppercase text-slate-400 leading-none">
                      Canal {canal.toLowerCase()}
                    </span>
                    <span className="text-lg font-bold tracking-[-0.02em] text-slate-900">
                      {min === max ? formatCOP(min) : `${formatCOP(min)} – ${formatCOP(max)}`}
                    </span>
                    <span className="text-xs text-slate-400">
                      por {unidad.toLowerCase()} · {delCanal.length} presentación{delCanal.length > 1 ? 'es' : ''}
                    </span>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-slate-400 mt-3 leading-relaxed">
              {PRICING.referenceDisclaimer}
            </p>
          </div>
        )}

        {/* Recharts sparkline */}
        {priceHistory.length > 0 && (
        <div aria-label={PRICING.trendLabel}>
          <p className="text-xs font-semibold tracking-[0.06em] uppercase text-slate-400 mb-4">
            {PRICING.trendLabel}
          </p>
          <div className="h-[180px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={datosGrafica} margin={{ top: 4, right: 4, bottom: 0, left: 4 }}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="hsl(213,85%,42%)" stopOpacity={0.18} />
                    <stop offset="95%" stopColor="hsl(213,85%,42%)" stopOpacity={0}    />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(214,20%,92%)" vertical={false} />
                <XAxis dataKey="period" tick={{ fontSize: 11, fill: 'hsl(220,10%,65%)' }} axisLine={false} tickLine={false} dy={6} />
                <YAxis
                  tickFormatter={v => `${Math.round(v / 1000)}k`}
                  tick={{ fontSize: 11, fill: 'hsl(220,10%,65%)' }}
                  axisLine={false} tickLine={false} dx={-4}
                />
                <Tooltip
                  formatter={(v: unknown, name: unknown) => [
                    formatCOP(v as number),
                    name === 'referencia' ? 'Referencia Clicsalud oct-2024 (por unidad)' : 'Precio SISMED',
                  ]}
                  contentStyle={{
                    background: 'white', border: '1px solid hsl(214,20%,90%)',
                    borderRadius: 10, boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
                    fontSize: 12,
                  }}
                />
                {maxRegulatedPrice && (
                  <ReferenceLine
                    y={maxRegulatedPrice}
                    stroke="hsl(38,95%,50%)"
                    strokeDasharray="4 4"
                    strokeWidth={1.5}
                    label={{ value: 'Precio máx.', position: 'insideTopRight', fontSize: 10, fill: 'hsl(38,95%,28%)' }}
                  />
                )}
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="hsl(213,85%,42%)"
                  strokeWidth={2.5}
                  fill="url(#priceGradient)"
                  dot={{ r: 4, fill: 'white', stroke: 'hsl(213,85%,42%)', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: 'hsl(213,85%,42%)', stroke: 'white', strokeWidth: 2 }}
                />
                {/* Punto vigente (Clicsalud) — serie aparte, no continúa la línea SISMED */}
                <Line
                  dataKey="referencia"
                  stroke="hsl(160,84%,30%)"
                  strokeWidth={0}
                  dot={{ r: 6, fill: 'hsl(160,84%,35%)', stroke: 'white', strokeWidth: 2 }}
                  activeDot={{ r: 7, fill: 'hsl(160,84%,30%)', stroke: 'white', strokeWidth: 2 }}
                  isAnimationActive={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>
        )}
      </div>
    </section>
  );
}
