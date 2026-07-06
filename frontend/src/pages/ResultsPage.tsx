import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { buscarMedicamentos, obtenerDetalle, type ApiMedicamento } from '../lib/api';
import type { MedicationDetail } from '../types/medication';
import MedicationProfileCard from '../components/medication/MedicationProfileCard';
import RiskAnalysisSection from '../components/medication/RiskAnalysisSection';
import PricingSection from '../components/medication/PricingSection';
import MedicationTimeline from '../components/medication/MedicationTimeline';
import RelatedMedications from '../components/medication/RelatedMedications';
import NotificationsSubscription from '../components/medication/NotificationsSubscription';

type Estado =
  | { fase: 'cargando' }
  | { fase: 'sin-resultados' }
  | { fase: 'error' }
  | { fase: 'ok'; data: MedicationDetail; coincidencias: ApiMedicamento[] };

export default function ResultsPage() {
  const { slug = '' } = useParams<{ slug: string }>();
  const consulta = decodeURIComponent(slug);
  const [estado, setEstado] = useState<Estado>({ fase: 'cargando' });

  useEffect(() => {
    let cancelado = false;
    setEstado({ fase: 'cargando' });

    (async () => {
      try {
        // El slug puede ser un expediente (navegación interna) o texto de búsqueda
        const esExpediente = /^\d+$/.test(consulta);
        let expediente: number;
        let coincidencias: ApiMedicamento[] = [];

        if (esExpediente) {
          expediente = Number(consulta);
        } else {
          coincidencias = await buscarMedicamentos(consulta, 8);
          if (!coincidencias.length) {
            if (!cancelado) setEstado({ fase: 'sin-resultados' });
            return;
          }
          expediente = coincidencias[0].expediente;
        }

        const data = await obtenerDetalle(expediente);
        if (!cancelado) setEstado({ fase: 'ok', data, coincidencias: coincidencias.slice(1) });
      } catch {
        if (!cancelado) setEstado({ fase: 'error' });
      }
    })();

    return () => {
      cancelado = true;
    };
  }, [consulta]);

  if (estado.fase === 'cargando') {
    return (
      <main id="main-content" className="min-h-[60vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-100 border-t-blue-600" />
      </main>
    );
  }

  if (estado.fase === 'sin-resultados' || estado.fase === 'error') {
    return (
      <main id="main-content">
        <div className="container">
          <div className="text-center py-20 px-6">
            <div className="text-[64px] mb-4" aria-hidden="true">💊</div>
            <h1 className="text-2xl font-bold text-slate-900 mb-3">
              {estado.fase === 'error' ? 'No pudimos consultar la información' : 'Medicamento no encontrado'}
            </h1>
            <p className="text-slate-500 mb-6">
              {estado.fase === 'error'
                ? 'Hubo un problema conectando con los datos. Intenta de nuevo en unos segundos.'
                : `No encontramos información para «${consulta}» en el catálogo CUM vigente de INVIMA. Intenta con el nombre genérico o el principio activo.`}
            </p>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 bg-primary text-white font-semibold text-base px-6 py-3 rounded-lg no-underline transition-all duration-150 hover:bg-primary-dark hover:-translate-y-px cursor-pointer"
            >
              ← Volver al inicio
            </Link>
          </div>
        </div>
      </main>
    );
  }

  const { profile, risk, pricing, timeline, alternatives } = estado.data;
  const hayPrecios = pricing.priceHistory.length > 0 || pricing.maxRegulatedPrice > 0;

  return (
    <main id="main-content" className="py-8 pb-16" aria-label={`Resultado: ${profile.name}`}>
      <div className="container">

        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm text-slate-400 mb-6 flex-wrap pt-5">
          <Link to="/dashboard" className="text-primary font-medium hover:underline cursor-pointer">Inicio</Link>
          <span aria-hidden="true" className="text-slate-400">›</span>
          <span aria-current="page" className="text-slate-400">{profile.name}</span>
        </nav>

        {/* Page heading */}
        <h1 className="text-[clamp(1.5rem,3vw,2rem)] font-bold text-slate-900 tracking-[-0.03em] mb-2">
          Resultado de Búsqueda
        </h1>
        <p className="text-sm text-slate-400 mb-4">
          Datos oficiales en vivo · INVIMA (CUM y Vitales No Disponibles), SISMED y CNPMDM vía datos.gov.co
        </p>

        {/* Otras coincidencias de la búsqueda */}
        {estado.coincidencias.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap mb-6">
            <span className="text-xs font-semibold text-slate-400">Otras coincidencias:</span>
            {estado.coincidencias.slice(0, 5).map((m) => (
              <Link
                key={m.expediente}
                to={`/medicamento/${m.expediente}`}
                className="text-xs text-primary bg-blue-50 border border-blue-100 rounded-full px-3 py-1 no-underline hover:bg-blue-100 transition-colors"
              >
                {(m.producto ?? '').toLowerCase().replace(/(^|\s)\S/g, (c) => c.toUpperCase())}
              </Link>
            ))}
          </div>
        )}

        {/* Two-column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_340px] gap-6 items-start">

          {/* Main column */}
          <div className="flex flex-col gap-6 min-w-0">
            <MedicationProfileCard profile={profile} />
            <RiskAnalysisSection risk={risk} />
            {hayPrecios ? (
              <>
                <PricingSection pricing={pricing} />
                <p className="text-xs text-slate-400 -mt-4 px-2">
                  Histórico de precios: SISMED 2017-2019 (referencia). Precio máximo: Circular 19 de 2024 (CNPMDM).
                </p>
              </>
            ) : (
              <section className="bg-white border border-slate-200 rounded-2xl shadow-card px-6 py-5">
                <h2 className="text-lg font-bold text-slate-900 mb-1">💹 Precios</h2>
                <p className="text-sm text-slate-500">
                  Este producto no tiene precios reportados en SISMED (2017-2019) ni precio máximo regulado vigente.
                </p>
              </section>
            )}
            {timeline.length > 0 && <MedicationTimeline events={timeline} />}
            {alternatives.length > 0 && <RelatedMedications alternatives={alternatives} />}
          </div>

          {/* Sticky sidebar */}
          <div className="flex flex-col gap-6 min-w-0 lg:sticky lg:top-[88px]">
            <NotificationsSubscription />
          </div>

        </div>
      </div>
    </main>
  );
}
