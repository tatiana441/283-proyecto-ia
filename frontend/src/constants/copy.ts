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
      href:        '/buscar',
      color:       'primary',
    },
    {
      id:          'alerts',
      title:       'Alertas de Escasez',
      description: 'Revisa las alertas activas de desabastecimiento en tiempo real.',
      icon:        '🚨',
      href:        '/alertas',
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

  bannerTitle:      'Monitoreo de riesgo de medicamentos impulsado por IA para Colombia',
  bannerSubtitle:   'Analizamos más de 15.000 registros sanitarios del INVIMA para darte información oportuna y confiable.',
  bannerCta:        'Conocer más',

  statsLabel:       'En tiempo real',
  stats: [
    { value: '15.240', label: 'Registros monitoreados' },
    { value: '342',   label: 'Alertas activas'         },
    { value: '98%',   label: 'Precisión del modelo IA' },
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
  trendLabel:         'Tendencia histórica de precios · SISMED 2017–2019',
  currencyLabel:      'COP',
  noDataLabel:        'Sin datos disponibles',
  sourceLabel:        'Fuente: Ministerio de Salud — Circular de precios',
  notRegulatedValue:  'No regulado',
  notRegulatedMeta:   'Este producto no está en la Circular de precios máximos vigente',
  educationBody:
    'El "último precio reportado" viene de SISMED, el sistema donde laboratorios y EPS reportan sus ventas; ' +
    'la serie disponible cubre 2017 a mediados de 2019, por eso la gráfica llega hasta ahí (es una referencia ' +
    'histórica, no el precio de farmacia de hoy). El "precio máximo regulado" sí es vigente: es el techo fijado ' +
    'por la Comisión Nacional de Precios (Circular 19 de 2024), que solo cubre los mercados intervenidos — ' +
    'alrededor del 30% de los productos. Si dice "No regulado", ese producto no tiene techo de precio.',
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
  subtitle: 'Miles de medicamentos monitoreados de forma continua para que nunca te enfrentes a un desabastecimiento inesperado.',
  stats: [
    {
      id: 'monitored',
      value: 14800,
      suffix: '+',
      label: 'Medicamentos monitoreados',
      sublabel: 'Productos farmacéuticos activos',
      color: 'blue',
    },
    {
      id: 'critical',
      value: 312,
      suffix: '',
      label: 'Medicamentos críticos',
      sublabel: 'Con seguimiento reforzado',
      color: 'red',
    },
    {
      id: 'datasets',
      value: 8,
      suffix: '',
      label: 'Conjuntos de datos',
      sublabel: 'Fuentes oficiales integradas',
      color: 'green',
    },
    {
      id: 'precision',
      value: 99,
      suffix: '%',
      label: 'Precisión de la IA',
      sublabel: 'Confianza en el análisis de riesgo',
      color: 'blue',
    },
  ],
};

// ── Demo de Medicamento (Landing Page) ───────────────────────────────────────
export const LANDING_DEMO = {
  badge: 'Vélo en acción',
  title: 'Ejemplo de monitoreo de medicamento',
  description: 'Así es un perfil de medicamento típico en MediWatch — claro, fácil de leer y diseñado para darte la información correcta de un vistazo.',
  checkItems: [
    'Disponibilidad actual y estado del stock',
    'Evaluación del riesgo de desabastecimiento con IA',
    'Historial de monitoreo cronológico',
    'Alternativas comparables si es necesario',
  ],
  ctaLabel: 'Ver perfil completo',
  // Mock card data
  card: {
    label: 'Perfil del medicamento',
    name: 'Losartán',
    description: 'Antagonista del receptor de angiotensina II',
    badges: [
      { text: 'En seguimiento', variant: 'blue' },
      { text: 'Riesgo medio',   variant: 'amber' },
    ],
    stats: [
      { value: '72%',  label: 'Disponibilidad', color: 'amber' },
      { value: '3',    label: 'Alertas (30d)',   color: 'red'   },
      { value: '+4,2%', label: 'Tendencia precio', color: 'red' },
    ],
    trendLabel: 'Tendencia de disponibilidad — 30 días',
    aiTitle: 'Análisis IA',
    aiText: '"Las tendencias recientes indican un aumento de la actividad de monitoreo. El suministro de los fabricantes principales muestra variabilidad. Considera hablar con tu farmacéutico sobre alternativas."',
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

