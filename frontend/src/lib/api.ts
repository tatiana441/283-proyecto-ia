// Cliente de la API MediWatch (FastAPI) + adaptadores a los tipos del frontend.
// El backend devuelve datos crudos de los datasets; aquí se mapean a
// MedicationDetail para que los componentes existentes no cambien.

import type {
  AlternativeMedication,
  MedicationDetail,
  MedicationProfile,
  PricePoint,
  PricingData,
  RiskAnalysis,
  RiskLevel,
  RiskTrend,
  TimelineEvent,
} from '../types/medication';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function get<T>(path: string): Promise<T> {
  const resp = await fetch(`${API_URL}${path}`);
  if (!resp.ok) throw new Error(`API ${resp.status}: ${path}`);
  return resp.json() as Promise<T>;
}

// ── Tipos de la API ──────────────────────────────────────────────────────────

export interface ApiMedicamento {
  expediente: number;
  producto: string | null;
  titular: string | null;
  estadoregistro: string | null;
  principios_activos: string[];
  atc: string | null;
  riesgo_score: number | null;
  riesgo_nivel: string | null;
}

export interface ApiRiesgo {
  principio_activo: string;
  mes: string;
  score: number;
  nivel: string;
  tendencia: string;
  factores: Record<string, unknown>;
  ai_insight?: string;
  prob_ml?: number | null;
}

export interface ApiStats {
  productos: number;
  principios_activos: number;
  solicitudes_vitales: number;
  pas_con_score: number;
  pas_riesgo_alto: number;
  mes_corte_riesgo: string | null;
  top_riesgo: ApiRiesgo[];
}

export interface ChatSource {
  dataset: string;
  herramienta: string;
  registros: number;
}

export interface ChatRespuesta {
  respuesta: string;
  sources: ChatSource[];
  herramientas_usadas: string[];
}

interface ApiDetalle {
  perfil: {
    expediente: number;
    producto: string | null;
    titular: string | null;
    registrosanitario: string | null;
    estadoregistro: string | null;
    principios_activos: string[];
    atc: string[] | null;
    descripcion_atc: string[] | null;
  };
  presentaciones: {
    cum_std: string;
    descripcioncomercial: string | null;
    formafarmaceutica: string | null;
    estadocum: string | null;
  }[];
  riesgo: ApiRiesgo | null;
  historial_solicitudes: {
    fecha_autorizacion: string | null;
    tipo_solicitud: string | null;
    solicitante_importador: string | null;
    principio_activo_1: string | null;
    cantidad_solicitada: number | null;
  }[];
  precios: {
    regulado_vigente: { pmax_institucional: number | null; pmax_comercial_final: number | null; circular: string | null }[];
    historico_sismed: { mes: string; tipo_reporte: string; precio_promedio: number | null }[];
    nota: string;
  };
  alternativas: { expediente: number; producto: string | null; titular: string | null }[];
}

// ── Endpoints ────────────────────────────────────────────────────────────────

export const buscarMedicamentos = (q: string, limit = 20) =>
  get<ApiMedicamento[]>(`/api/medicamentos?search=${encodeURIComponent(q)}&limit=${limit}`);

export const obtenerStats = () => get<ApiStats>('/api/stats');

export const topRiesgo = (n = 25) => get<ApiRiesgo[]>(`/api/riesgo/top?n=${n}`);

export async function enviarChat(pregunta: string, historial: { role: string; content: string }[], userId?: string) {
  const resp = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pregunta, historial, user_id: userId ?? null }),
  });
  if (!resp.ok) throw new Error(`API ${resp.status}: /api/chat`);
  return resp.json() as Promise<ChatRespuesta>;
}

// ── Adaptador: respuesta de la API → MedicationDetail del frontend ──────────

const NIVEL_A_LEVEL: Record<string, RiskLevel> = {
  bajo: 'low', medio: 'monitor', alto: 'high', critico: 'high',
};
const TENDENCIA_A_TREND: Record<string, RiskTrend> = {
  subiendo: 'increasing', bajando: 'decreasing', estable: 'stable',
};

function titleCase(s: string | null): string {
  if (!s) return '—';
  return s.toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase());
}

export async function obtenerDetalle(expediente: number): Promise<MedicationDetail> {
  const d = await get<ApiDetalle>(`/api/medicamentos/${expediente}`);

  const profile: MedicationProfile = {
    id: String(d.perfil.expediente),
    name: titleCase(d.perfil.producto),
    activeIngredient: titleCase(d.perfil.principios_activos.join(', ')),
    therapeuticCategory: titleCase(d.perfil.descripcion_atc?.[0] ?? null),
    pharmaceuticalForm: titleCase(d.presentaciones[0]?.formafarmaceutica ?? null),
    administrationRoute: '—',
    regulatoryStatus: d.perfil.estadoregistro?.toLowerCase().includes('vigente') ? 'Aprobado' : 'En revisión',
    atcCode: d.perfil.atc?.[0] ?? undefined,
    manufacturer: titleCase(d.perfil.titular),
  };

  const risk: RiskAnalysis = d.riesgo
    ? {
        score: d.riesgo.score,
        level: NIVEL_A_LEVEL[d.riesgo.nivel] ?? 'monitor',
        trend: TENDENCIA_A_TREND[d.riesgo.tendencia] ?? 'stable',
        aiInsight: d.riesgo.ai_insight ?? '',
        lastUpdated: d.riesgo.mes,
        reportingPeriods: Number(d.riesgo.factores?.solicitudes_12m ?? 0),
        mlProbability: d.riesgo.prob_ml ?? null,
      }
    : {
        score: 0,
        level: 'low',
        trend: 'stable',
        aiInsight:
          'Este medicamento no registra solicitudes de importación excepcional ante INVIMA, ' +
          'por lo que no presenta señales de desabastecimiento en los datos oficiales.',
        lastUpdated: new Date().toISOString().slice(0, 7),
      };

  // Precios: histórico SISMED (VENTA) + techo regulado vigente
  const ventas = d.precios.historico_sismed.filter(
    (p) => p.tipo_reporte === 'VENTA' && p.precio_promedio != null,
  );
  const priceHistory: PricePoint[] = ventas.map((p) => ({
    period: p.mes,
    price: Math.round(p.precio_promedio!),
  }));
  const ultimoPrecio = priceHistory.length ? priceHistory[priceHistory.length - 1].price : 0;
  const regulado = d.precios.regulado_vigente[0];
  const pricing: PricingData = {
    averageMarketPrice: ultimoPrecio,
    maxRegulatedPrice: Math.round(regulado?.pmax_comercial_final ?? regulado?.pmax_institucional ?? 0),
    currency: 'COP',
    priceHistory,
  };

  const timeline: TimelineEvent[] = d.historial_solicitudes.slice(0, 8).map((h, i) => ({
    id: `sol-${i}`,
    date: h.fecha_autorizacion?.slice(0, 10) ?? '—',
    title: titleCase(h.tipo_solicitud) || 'Solicitud de importación',
    description: `${titleCase(h.solicitante_importador)} — ${titleCase(h.principio_activo_1)}${
      h.cantidad_solicitada ? ` (${h.cantidad_solicitada.toLocaleString('es-CO')} unidades)` : ''
    }`,
    type: h.tipo_solicitud?.toUpperCase().includes('URGENCIA') ? 'alert' : 'shortage',
  }));

  const alternatives: AlternativeMedication[] = d.alternativas.map((a) => ({
    id: String(a.expediente),
    name: titleCase(a.producto),
    activeIngredient: titleCase(a.titular),
    riskLevel: 'low',
    riskScore: 0,
    similarity: 'Mismo principio activo',
  }));

  return { profile, risk, pricing, timeline, alternatives };
}
