import { useEffect, useRef, useState } from 'react';
import type { RiskAnalysis, RiskLevel, RiskTrend } from '../../types/medication';
import { RISK } from '../../constants/copy';

// ─── SVG gauge constants ──────────────────────────────────────────────────────
const GAUGE_R   = 90;
const GAUGE_CX  = 110;
const GAUGE_CY  = 115;
const CIRCUMFERENCE = Math.PI * GAUGE_R; // half-circle ≈ 283

// ─── Lookup tables (complete class strings for Tailwind scanner) ───────────────
const LEVEL_CLASSES: Record<RiskLevel, { pill: string; score: string; dot: string }> = {
  low:     { pill: 'bg-low-bg text-low-text',          score: 'text-low',     dot: 'bg-low'     },
  monitor: { pill: 'bg-monitor-bg text-monitor-text',  score: 'text-monitor', dot: 'bg-monitor' },
  high:    { pill: 'bg-high-bg text-high-text',        score: 'text-high',    dot: 'bg-high'    },
};

const TREND_CLASSES: Record<RiskTrend, { value: string; arrow: string }> = {
  stable:     { value: 'text-primary',  arrow: ''                                              },
  increasing: { value: 'text-high',     arrow: 'animate-[bounce-up_1.4s_ease-in-out_infinite]'  },
  decreasing: { value: 'text-low',      arrow: 'animate-[bounce-down_1.4s_ease-in-out_infinite]'},
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function describeArc(cx: number, cy: number, r: number): string {
  const x1 = cx + r * Math.cos(Math.PI); // left
  const y1 = cy + r * Math.sin(Math.PI);
  const x2 = cx + r * Math.cos(0);       // right
  const y2 = cy + r * Math.sin(0);
  return `M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`;
}

function scoreToLevel(score: number): RiskLevel {
  if (score < 34) return 'low';
  if (score < 67) return 'monitor';
  return 'high';
}

function scoreToOffset(score: number): number {
  return CIRCUMFERENCE - (Math.max(0, Math.min(100, score)) / 100) * CIRCUMFERENCE;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' });
}

// ─── Component ────────────────────────────────────────────────────────────────
interface RiskAnalysisSectionProps {
  risk: RiskAnalysis;
}

export default function RiskAnalysisSection({ risk }: RiskAnalysisSectionProps) {
  const { score, trend, aiInsight, lastUpdated } = risk;
  const level = scoreToLevel(score);
  const cls   = LEVEL_CLASSES[level];
  const trendCls = TREND_CLASSES[trend];

  const [showInfo, setShowInfo] = useState(false);
  const [animated, setAnimated] = useState(false);
  const progressRef = useRef<SVGPathElement>(null);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 80);
    return () => clearTimeout(t);
  }, []);

  const arcPath    = describeArc(GAUGE_CX, GAUGE_CY, GAUGE_R);
  const dashOffset = animated ? scoreToOffset(score) : CIRCUMFERENCE;

  const { label: levelLabel } = RISK.levels[level];
  const { label: trendLabel, icon: trendIcon } = RISK.trends[trend];

  return (
    <section
      className="bg-white border border-slate-200 rounded-2xl shadow-card overflow-hidden"
      aria-labelledby="risk-section-title"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <span className="text-[22px]" aria-hidden="true">🧠</span>
          <h2 id="risk-section-title" className="text-lg font-bold text-slate-900 tracking-[-0.02em]">
            {RISK.sectionTitle}
          </h2>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <time
            className="text-xs text-slate-400 font-medium"
            dateTime={lastUpdated}
            aria-label={`${RISK.lastUpdated}: ${formatDate(lastUpdated)}`}
          >
            {RISK.lastUpdated}: {formatDate(lastUpdated)}
          </time>
          <button
            className="text-xs font-semibold text-primary bg-primary-bg px-3 py-1.5 rounded-full border border-primary/20 transition-colors hover:bg-primary hover:text-white cursor-pointer"
            onClick={() => setShowInfo(p => !p)}
            aria-expanded={showInfo}
            aria-controls="risk-edu-panel"
          >
            {showInfo ? '✕ Cerrar' : '¿Qué es esto?'}
          </button>
        </div>
      </div>

      {/* Collapsible education panel */}
      {showInfo && (
        <div
          id="risk-edu-panel"
          className="mx-6 mt-4 bg-primary-bg border border-primary/15 border-l-4 border-l-primary rounded-lg p-4 text-sm text-slate-500 leading-[1.7] animate-[fade-in_0.25s_ease]"
          role="region"
          aria-label="Cómo se calcula el puntaje de riesgo"
        >
          {RISK.educationBody}
        </div>
      )}

      {/* Two-column body */}
      <div className="grid grid-cols-1 md:grid-cols-2">

        {/* ── Left: Gauge ── */}
        <div className="flex flex-col items-center justify-center px-6 py-8 border-b md:border-b-0 md:border-r border-slate-200 gap-5">

          {/* SVG gauge — stroke props must stay in CSS */}
          <div className="relative w-[220px] h-[130px]">
            <svg
              width="220" height="130"
              viewBox="0 0 220 130"
              className="overflow-visible"
              role="img"
              aria-label={`Puntaje de riesgo: ${score} de 100. Nivel: ${levelLabel}`}
            >
              <path className="gauge-track" d={arcPath} />
              <path
                ref={progressRef}
                className="gauge-progress"
                d={arcPath}
                data-level={level}
                strokeDasharray={CIRCUMFERENCE}
                strokeDashoffset={dashOffset}
              />
            </svg>

            {/* Score overlay */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-center flex flex-col items-center" aria-hidden="true">
              <span className={`text-5xl font-bold leading-none tracking-[-0.04em] transition-colors duration-600 ${cls.score}`}>
                {score}
              </span>
              <span className="text-xs text-slate-400 font-medium tracking-[0.04em]">{RISK.scoreLabel}</span>
            </div>
          </div>

          {/* Scale labels */}
          <div className="flex justify-between w-[220px] text-xs text-slate-400 font-medium" aria-hidden="true">
            <span>0</span><span>50</span><span>100</span>
          </div>

          {/* Risk pill */}
          <div
            className={`inline-flex items-center gap-2 px-5 py-2 rounded-full text-sm font-semibold tracking-[0.01em] ${cls.pill} ${level === 'high' ? 'animate-[risk-pulse_2.5s_ease-in-out_infinite]' : ''}`}
            role="status"
            aria-label={`Nivel de riesgo: ${levelLabel}`}
          >
            <span className={`w-2 h-2 rounded-full ${cls.dot}`} aria-hidden="true" />
            {levelLabel}
          </div>
        </div>

        {/* ── Right: AI Insight (junto al velocímetro) + Trend ── */}
        <div className="flex flex-col px-6 py-6 gap-5">

          {/* AI insight */}
          <div
            className="flex flex-col gap-3 bg-linear-to-br from-primary-bg to-[hsl(213,60%,95%)] border border-primary/10 border-l-4 border-l-primary rounded-lg px-5 py-4 flex-1"
            role="region"
            aria-labelledby="ai-insight-title"
          >
            <div className="flex items-center gap-2">
              <span className="text-lg" aria-hidden="true">{RISK.aiInsightIcon}</span>
              <h3 id="ai-insight-title" className="text-sm font-semibold text-primary tracking-[0.01em]">
                {RISK.aiInsightTitle}
              </h3>
            </div>
            <p className="text-sm text-slate-500 leading-[1.7]">{aiInsight}</p>
          </div>

          {/* Trend card */}
          <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-5 py-4 gap-3">
            <span className="text-sm font-medium text-slate-500">Tendencia actual</span>
            <div
              className={`flex items-center gap-2 text-sm font-semibold ${trendCls.value}`}
              aria-label={`Tendencia: ${trendLabel}`}
            >
              <span className={`text-xl font-bold inline-block ${trendCls.arrow}`} aria-hidden="true">
                {trendIcon}
              </span>
              {trendLabel}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
