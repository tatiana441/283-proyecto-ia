// ─── MediAlerta Colombia — Spanish Copy Constants ────────────────────────────
// All user-facing strings in Colombian Spanish, centralized for easy localization.
import type { FeatureCardData } from '../components/shared/FeatureCard';

export const APP_NAME = 'MediWatch';
export const APP_TAGLINE = 'Monitoreo inteligente de medicamentos para Colombia';

// ── Navbar ──────────────────────────────────────────────────────────────────
export const NAV = {
  home:             'Inicio',
  categories:       'Categorías',
  logoAlt:          'MediWatch - Ir al inicio',
  skipToContent:    'Saltar al contenido principal',
};

// ── Home Page ────────────────────────────────────────────────────────────────
export const HOME = {
  heroTitle:        'Medicamentos Seguros',
  spanTitle:        'para todos los Colombianos',
  heroSubtitle:     'Consulta disponibilidad, alertas de escasez y análisis de riesgo en tiempo real para los medicamentos que necesitas.',
  searchPlaceholder:'Busca un medicamento o principio activo',
  searchButton:     'Buscar',
  exampleLabel:     'Búsquedas frecuentes:',
  exampleTags:      ['Losartán', 'Metformina', 'Insulina', 'Omeprazol'],

  quickActionsTitle:'Acciones Rápidas',
  actions: [
    {
      id:          'search',
      title:       'Búsqueda de Medicamentos',
      description: 'Consulta disponibilidad y riesgo por nombre o principio activo.',
      icon:        '🔍',
      href:        '/dashboard#buscar',
      color:       'primary',
    },
    {
      id:          'alerts',
      title:       'Alertas de Escasez',
      description: 'Revisa los medicamentos en riesgo alto o crítico ahora mismo.',
      icon:        '🚨',
      href:        '/alto-riesgo',
      color:       'high',
    },
    {
      id:          'categories',
      title:       'Categorías Terapéuticas',
      description: 'Explora medicamentos por grupo terapéutico o patología.',
      icon:        '📋',
      href:        '/categorias',
      color:       'low',
    },
  ],

};

// ── Risk Analysis Section ────────────────────────────────────────────────────
export const RISK = {
  sectionTitle:     'Análisis de Riesgo IA',
  sectionSubtitle:  'Actualizado con los últimos datos del INVIMA',
  scoreLabel:       'Puntuación de Riesgo',
  lastUpdated:      'Última actualización',

  levels: {
    low:     { label: 'Riesgo Bajo',                    short: 'Bajo'       },
    monitor: { label: 'En Monitoreo',                   short: 'Monitoreo'  },
    high:    { label: 'Alto Riesgo de Desabastecimiento', short: 'Alto Riesgo'},
  },

  trends: {
    stable:     { label: 'Estable',             icon: '→' },
    increasing: { label: 'Riesgo en aumento',   icon: '↑' },
    decreasing: { label: 'Riesgo en disminución', icon: '↓' },
  },

  aiInsightTitle:   'Análisis de Inteligencia Artificial',
  aiInsightIcon:    '🤖',
  predictionLabel:  'Predicción IA · próximos 3 meses',
  predictionMeta:   'Probabilidad de nuevas solicitudes de escasez, según regresión logística validada con backtest (AUC 0,79)',
  educationBody:
    'Cuando un medicamento escasea en Colombia, los hospitales piden a INVIMA importarlo por vía excepcional ' +
    '("Medicamentos Vitales No Disponibles"); cada solicitud es una señal de escasez. El puntaje 0–100 combina ' +
    'cinco factores sobre esas solicitudes: frecuencia (35%), tendencia al alza (25%), qué tan recientes son (20%), ' +
    'cuántos solicitantes distintos hay (10%) y su urgencia (10%). De 0 a 33 el riesgo es bajo, de 34 a 66 en ' +
    'observación y de 67 en adelante alto. El método fue validado con un backtest temporal (AUC 0,79).',
};

// ── Medication Profile Card ──────────────────────────────────────────────────
export const PROFILE = {
  sectionTitle:     'Perfil del Medicamento',
  fields: {
    name:               'Nombre del medicamento',
    activeIngredient:   'Principio activo',
    therapeuticCategory:'Categoría terapéutica',
    pharmaceuticalForm: 'Forma farmacéutica',
    administrationRoute:'Vía de administración',
    regulatoryStatus:   'Estado regulatorio',
    atcCode:            'Código ATC',
    manufacturer:       'Fabricante',
  },
  statusColors: {
    'Aprobado':    'low',
    'En revisión': 'monitor',
    'Suspendido':  'high',
    'Retirado':    'high',
  } as Record<string, string>,
};

// ── Pricing Section ──────────────────────────────────────────────────────────
export const PRICING = {
  sectionTitle:       'Información de Precios',
  averageLabel:       'Último precio reportado (SISMED)',
  regulatedLabel:     'Precio máximo regulado',
  trendLabel:         'Línea de tiempo de precios · SISMED 2017–2019 + referencia vigente (punto verde, oct 2024)',
  currencyLabel:      'COP',
  noDataLabel:        'Sin datos disponibles',
  sourceLabel:        'Fuente: Ministerio de Salud — Circular de precios',
  notRegulatedValue:  'No regulado',
  notRegulatedMeta:   'Este producto no está en la Circular de precios máximos vigente',
  referenceTitle:     'Precio de referencia vigente por unidad · Termómetro Clicsalud (MinSalud, oct 2024)',
  referenceDisclaimer:
    'ℹ️ Valor de referencia con corte a octubre de 2024, la última publicación oficial disponible. ' +
    'El precio real en 2026 puede variar según la entidad, el canal, negociaciones y descuentos; ' +
    'úsalo como orientación, no como precio final de compra.',
  educationBody:
    'El "precio de referencia por unidad" es el más actual: viene del Termómetro de Precios de Clicsalud ' +
    '(Ministerio de Salud, corte octubre 2024) e indica cuánto debería costar cada tableta o ampolla en el ' +
    'canal comercial (farmacias) e institucional (EPS/hospitales). El "precio máximo regulado" es el techo ' +
    'legal fijado por la Comisión Nacional de Precios (Circular 19 de 2024), que solo cubre mercados ' +
    'intervenidos (~30% de los productos): si dice "No regulado", ese producto no tiene techo. La gráfica ' +
    'histórica viene de SISMED, donde la industria reporta sus ventas; la serie pública cubre 2017 a mediados ' +
    'de 2019 — el Estado no ha publicado precios transaccionales más recientes.',
};

// ── Timeline ─────────────────────────────────────────────────────────────────
export const TIMELINE = {
  sectionTitle:       'Historial del Medicamento',
  typeLabels: {
    approval:    'Aprobación regulatoria',
    monitoring:  'Inicio de monitoreo',
    shortage:    'Alerta de desabastecimiento',
    resolved:    'Situación normalizada',
    alert:       'Alerta activa',
  },
};

// ── Related Medications ──────────────────────────────────────────────────────
export const RELATED = {
  sectionTitle:       'Alternativas y Educación',
  alternativesTitle:  'Medicamentos alternativos',
  alternativesSubtitle:'Basado en principio activo y categoría terapéutica',
  educationTitle:     '¿Qué significa el puntaje de riesgo?',
  educationBody: `El puntaje de riesgo de desabastecimiento es calculado por un modelo de IA 
que analiza datos históricos de importación, registros INVIMA, 
reportes de fabricantes y tendencias de consumo nacional.

Un puntaje de 0 indica disponibilidad total. Un puntaje de 100 indica 
desabastecimiento crítico inminente. Este sistema complementa — 
pero no reemplaza — la orientación de su médico tratante.`,
  consultLabel:       'Consulte siempre con su médico antes de cambiar su medicamento.',
};

// ── Notifications ─────────────────────────────────────────────────────────────
export const NOTIFICATIONS = {
  sectionTitle:       'Suscripciones y Alertas',
  sectionSubtitle:    'Recibe notificaciones personalizadas sobre este medicamento',
  emailTab:           'Correo electrónico',
  whatsappTab:        'WhatsApp',
  emailPlaceholder:   'tucorreo@ejemplo.com',
  whatsappPlaceholder:'3XX XXX XXXX',
  alertTypes: [
    { id: 'risk',     label: 'Cambios en el nivel de riesgo'    },
    { id: 'price',    label: 'Variaciones de precio'            },
    { id: 'shortage', label: 'Alertas de desabastecimiento'     },
    { id: 'updates',  label: 'Actualizaciones regulatorias'     },
  ],
  subscribeButton:    'Suscribirse',
  successMessage:     '¡Suscripción exitosa! Te notificaremos sobre cambios importantes.',
  privacyNote:        'Tus datos son tratados conforme a la Ley 1581 de 2012 (Habeas Data).',
};

// ── Cómo Funciona (Landing Page) ─────────────────────────────────────────────
export const HOW_IT_WORKS = {
  badge: 'Simple y claro',
  title: 'Cómo Funciona',
  subtitle: 'Tres pasos sencillos para mantenerte informado sobre tus medicamentos.',
  steps: [
    {
      id: '01',
      title: 'Busca',
      description: 'Escribe el nombre de cualquier medicamento y accede al instante a su estado de monitoreo y disponibilidad.',
      iconType: 'search',
    },
    {
      id: '02',
      title: 'Analiza',
      description: 'Consulta indicadores de riesgo, estado de seguimiento, información de precios y tendencias históricas de forma clara.',
      iconType: 'analyze',
    },
    {
      id: '03',
      title: 'Mantente informado',
      description: 'Recibe alertas personalizadas y recomendaciones con inteligencia artificial sobre los medicamentos que más te importan.',
      iconType: 'info',
    },
  ],
};

// ── Hero (Landing Page) ──────────────────────────────────────────────────────
export const LANDING_HERO = {
  badge: 'Basado en datos oficiales de salud pública',
  titlePrefix: 'Conoce el estado de tu medicamento ',
  titleHighlight: 'antes de necesitarlo.',
  description: 'MediWatch ayuda a los ciudadanos a monitorear la disponibilidad de medicamentos, identificar riesgos de desabastecimiento y acceder a información farmacéutica fiable mediante datos oficiales de salud pública.',
  ctaPrimary: 'Iniciar Sesión',
  ctaSecondary: 'Cómo funciona',
  illustrationAlt: 'Ciudadano y asistente médica analizando panel de salud',
};

// ── Funcionalidades (Landing Page) ───────────────────────────────────────────
export const LANDING_FEATURES = {
  badge: 'Lo que ofrecemos',
  title: 'Funcionalidades principales',
  subtitle: 'Todo lo que necesitas para estar al tanto de tus medicamentos — claro, accesible y siempre actualizado.',
  items: [
    {
      id: 'search',
      iconType: 'search',
      accent: 'blue',
      title: 'Búsqueda de medicamentos',
      description: 'Encuentra cualquier medicamento al instante por nombre, principio activo o enfermedad. Los resultados son claros y fáciles de entender.',
    },
    {
      id: 'risk',
      iconType: 'risk',
      accent: 'red',
      title: 'Monitoreo de riesgos',
      description: 'Evaluación del riesgo de desabastecimiento en tiempo real basada en datos de la cadena de suministro y alertas oficiales.',
    },
    {
      id: 'price',
      iconType: 'price',
      accent: 'green',
      title: 'Información de precios',
      description: 'Consulta los precios actuales en farmacias y comprende los cambios que pueden afectar tu acceso a los medicamentos.',
    },
    {
      id: 'history',
      iconType: 'history',
      accent: 'purple',
      title: 'Historial del medicamento',
      description: 'Sigue el historial completo de disponibilidad, alertas y estado regulatorio de un medicamento a lo largo del tiempo.',
    },
    {
      id: 'ai',
      iconType: 'ai',
      accent: 'orange',
      title: 'Análisis con IA',
      description: 'Nuestra IA analiza patrones de múltiples fuentes para detectar señales de alerta antes de que se produzca un desabastecimiento.',
    },
    {
      id: 'alert',
      iconType: 'alert',
      accent: 'teal',
      title: 'Alertas personalizadas',
      description: 'Configura alertas para tus medicamentos y recibe notificaciones claras cuando algo cambia.',
    },
  ],
} satisfies { badge: string; title: string; subtitle: string; items: FeatureCardData[] };

// ── Estadísticas de Impacto (Landing Page) ───────────────────────────────────
export const LANDING_STATS = {
  badge: 'Impacto Real',
  title: 'Por qué importa MediWatch',
  subtitle: 'Cifras en vivo desde datos.gov.co: el catálogo completo de INVIMA y cada autorización de importación de urgencia, actualizados cada semana.',
  // Valores de respaldo (corte 2026-07) — la página los reemplaza con /api/stats en vivo
  stats: [
    {
      id: 'productos',
      value: 9655,
      suffix: '',
      label: 'Productos vigentes monitoreados',
      sublabel: 'Catálogo CUM de INVIMA, actualizado desde datos.gov.co',
      color: 'blue',
    },
    {
      id: 'solicitudes',
      value: 9601,
      suffix: '',
      label: 'Autorizaciones de importación analizadas',
      sublabel: 'Medicamentos Vitales No Disponibles (señal de escasez)',
      color: 'red',
    },
    {
      id: 'monitoreados',
      value: 601,
      suffix: '',
      label: 'Principios activos con score de riesgo',
      sublabel: 'Modelo validado con backtest temporal',
      color: 'blue',
    },
    {
      id: 'riesgo',
      value: 156,
      suffix: '',
      label: 'En riesgo alto o crítico',
      sublabel: 'Score ≥ 50: señales recurrentes y recientes de escasez',
      color: 'green',
    },
  ],
};

// ── Demo de Medicamento (Landing Page) ───────────────────────────────────────
export const LANDING_DEMO = {
  badge: 'Vélo en acción',
  title: 'Ejemplo de monitoreo de medicamento',
  description: 'Así es un perfil de medicamento típico en MediWatch — claro, fácil de leer y diseñado para darte la información correcta de un vistazo.',
  checkItems: [
    'Score de riesgo 0-100 con sus factores explicados',
    'Predicción IA validada: probabilidad de escasez a 3 meses',
    'Precios de 3 fuentes oficiales (referencia 2024, techo regulado e histórico)',
    'Alternativas con el mismo principio activo',
  ],
  ctaLabel: 'Ver perfil completo',
  // Ejemplo ilustrativo con la forma real del perfil (datos como los de lidocaína, corte 2026-05)
  card: {
    label: 'Perfil del medicamento',
    name: 'Lidocaína Clorhidrato',
    description: 'Anestésico local — con solicitudes de importación de urgencia',
    badges: [
      { text: 'Vigilancia activa', variant: 'blue' },
      { text: 'Riesgo crítico',    variant: 'amber' },
    ],
    stats: [
      { value: '89,7', label: 'Score de riesgo',    color: 'red'   },
      { value: '61',   label: 'Solicitudes (12 m)', color: 'amber' },
      { value: '100%', label: 'Predicción IA (3 m)', color: 'red'  },
    ],
    trendLabel: 'Solicitudes de importación — últimos 12 meses',
    aiTitle: 'Análisis IA',
    aiText: '"El principio activo registra 61 solicitudes de importación excepcional de 19 solicitantes en 12 meses, con tendencia al alza. Los factores que más pesan son la frecuencia y la tendencia reciente. Fuente: INVIMA — Vitales No Disponibles."',
  },
};

// ── Personas / Audiencias (Landing Page) ──────────────────────────────────────
export const LANDING_PERSONAS = {
  badge: 'Pensado para ti',
  title: 'Diseñado para pacientes y cuidadores',
  subtitle: 'MediWatch fue diseñado para que la información sobre medicamentos sea más fácil de entender para todos, independientemente de la edad o la experiencia tecnológica.',
  personas: [
    {
      id: 'elderly',
      emoji: '🧓',
      title: 'Personas mayores',
      description: 'Texto grande, navegación sencilla e indicaciones visuales claras hacen que MediWatch sea cómodo y fácil de usar cada día.',
    },
    {
      id: 'chronic',
      emoji: '💊',
      title: 'Pacientes con enfermedades crónicas',
      description: 'Sigue de forma continua tus medicamentos esenciales y recibe alertas antes de que un desabastecimiento afecte tu tratamiento.',
    },
    {
      id: 'caregiver',
      emoji: '🤝',
      title: 'Familiares y cuidadores',
      description: 'Monitorea los medicamentos de tus seres queridos y anticípate a posibles problemas de suministro, todo en un solo lugar.',
    },
  ],
};

// ── Confianza y Transparencia (Landing Page) ──────────────────────────────────
export const LANDING_TRUST = {
  badge: 'Puedes contar con nosotros',
  title: 'Confianza y transparencia',
  subtitle: 'MediWatch se basa en datos públicos, metodología abierta y un compromiso firme con tu privacidad.',
  pillars: [
    {
      id: 'official-data',
      iconType: 'database',
      accent: 'blue',
      title: 'Datos oficiales de salud pública',
      description: 'Todos los datos provienen directamente de organismos gubernamentales y agencias reguladoras.',
    },
    {
      id: 'transparent',
      iconType: 'methodology',
      accent: 'teal',
      title: 'Metodología transparente',
      description: 'Nuestro proceso de evaluación de riesgos está completamente documentado y disponible para el público.',
    },
    {
      id: 'ai-assisted',
      iconType: 'ai-check',
      accent: 'orange',
      title: 'Análisis asistido por IA',
      description: 'La inteligencia artificial detecta patrones — los profesionales verifican cada alerta.',
    },
    {
      id: 'secure',
      iconType: 'shield',
      accent: 'purple',
      title: 'Plataforma segura',
      description: 'No almacenamos datos personales de salud. Tu privacidad está protegida por diseño.',
    },
  ],
  sourcesTitle: 'Fuentes de datos integradas',
  source:'Toda la información presentada es recopilada, procesada y actualizada a partir de los conjuntos de datos públicos suministrados por el Instituto Nacional de Vigilancia de Medicamentos y Alimentos (INVIMA) y el Ministerio de Salud de Colombia.'
};

