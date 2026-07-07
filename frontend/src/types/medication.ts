// ─── MediAlerta Colombia — Shared Types ───────────────────────────────────────

export type RiskLevel = 'low' | 'monitor' | 'high';
export type RiskTrend = 'stable' | 'increasing' | 'decreasing';
export type NotificationChannel = 'email' | 'whatsapp';

export interface MedicationProfile {
  id: string;
  name: string;
  activeIngredient: string;
  therapeuticCategory: string;
  pharmaceuticalForm: string;
  administrationRoute: string;
  regulatoryStatus: 'Aprobado' | 'En revisión' | 'Suspendido' | 'Retirado';
  atcCode?: string;
  manufacturer?: string;
}

export interface RiskAnalysis {
  score: number; // 0–100
  level: RiskLevel;
  trend: RiskTrend;
  aiInsight: string;
  lastUpdated: string; // ISO date string
  reportingPeriods?: number; // # of periods with increased demand
  mlProbability?: number | null; // prob. (0-1) de nuevas solicitudes en 3 meses — modelo validado
}

export interface PricePoint {
  period: string; // e.g. "Ene 2024"
  price: number;  // in COP
}

export interface PricingData {
  averageMarketPrice: number;    // COP
  maxRegulatedPrice: number;     // COP
  currency: 'COP';
  priceHistory: PricePoint[];
}

export interface TimelineEvent {
  id: string;
  date: string;         // "YYYY-MM-DD"
  title: string;
  description: string;
  type: 'approval' | 'monitoring' | 'shortage' | 'resolved' | 'alert';
}

export interface AlternativeMedication {
  id: string;
  name: string;
  activeIngredient: string;
  riskLevel: RiskLevel;
  riskScore: number;
  similarity: 'Mismo principio activo' | 'Misma categoría terapéutica' | 'Mecanismo similar';
}

export interface MedicationDetail {
  profile: MedicationProfile;
  risk: RiskAnalysis;
  pricing: PricingData;
  timeline: TimelineEvent[];
  alternatives: AlternativeMedication[];
}
