"use client";

import { useQuery } from "@tanstack/react-query";
import { HelpCircle, Sparkles, MessageSquare, Clock, MapPin, CreditCard, ShieldCheck } from "lucide-react";

import { DashboardPageLayout } from "@/components/layout/DashboardPageLayout";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card/card";
import { Badge } from "@/components/ui/badge/badge";
import RobotPymio from "@/components/icons/robot-pymio";
import { fetchFaqs } from "@/services/faq-api";
import { fetchNegocio } from "@/services/negocio-api";

export default function FaqPage() {
  const { data: faqs = [] } = useQuery({
    queryKey: ["faqs"],
    queryFn: fetchFaqs,
  });

  const { data: negocio } = useQuery({
    queryKey: ["negocio"],
    queryFn: fetchNegocio,
  });

  return (
    <DashboardPageLayout>
      <PageHeader
        icon={<HelpCircle className="size-5" />}
        title="Preguntas Frecuentes (FAQs)"
        subtitle="Módulo de información del local y conocimiento para el chatbot de WhatsApp"
      />

      <div className="space-y-6">
        {/* Banner principal Pymio Branding */}
        <Card className="border-primary/20 bg-accent/40 overflow-hidden relative">
          <CardContent className="p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-3 max-w-xl text-center md:text-left">
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
                <Badge variant="default" className="bg-primary text-primary-foreground font-semibold">
                  MÓDULO ACTIVO
                </Badge>
                <Badge variant="outline" className="border-primary/40 text-primary">
                  <Sparkles className="size-3 mr-1" /> IA & RAG Próximamente
                </Badge>
              </div>

              <h2 className="text-xl md:text-2xl font-bold tracking-tight text-foreground">
                Base de Conocimiento de Pymio
              </h2>

              <p className="text-sm text-muted-foreground leading-relaxed">
                Tus clientes pueden consultar automáticamente esta información desde el menú de WhatsApp. Pymio responderá instantáneamente tus horarios, dirección, métodos de pago y preguntas frecuentes.
              </p>
            </div>

            <div className="shrink-0 flex items-center justify-center bg-card rounded-2xl p-4 shadow-sm border border-border">
              <RobotPymio className="h-28 w-auto text-primary" />
            </div>
          </CardContent>
        </Card>

        {/* Datos automáticos del negocio */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <Clock className="size-4 text-primary" /> Horarios de Atención
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground font-medium">
                {negocio?.horarios || "Lunes a Sábados de 09:00 a 20:00"}
              </p>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <MapPin className="size-4 text-primary" /> Dirección Comercial
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground font-medium">
                {negocio?.direccion || negocio?.contacto || "Consultar en el local"}
              </p>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2">
                <CreditCard className="size-4 text-primary" /> Medios de Pago
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground font-medium">
                Efectivo, Tarjetas de Crédito / Débito, Transferencia
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Listado de Preguntas Frecuentes */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <MessageSquare className="size-4 text-primary" /> Preguntas Frecuentes Activas ({faqs.length})
            </CardTitle>
            <CardDescription>
              Estas respuestas se envían automáticamente cuando el cliente selecciona la consulta en WhatsApp.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {faqs.length === 0 ? (
              <div className="py-8 text-center text-sm text-muted-foreground">
                No hay preguntas frecuentes registradas aún. El chatbot responderá con la información general de tu negocio.
              </div>
            ) : (
              faqs.map((faq) => (
                <div key={faq.id} className="rounded-lg border border-border p-4 space-y-1.5 bg-muted/20">
                  <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <ShieldCheck className="size-4 text-primary shrink-0" />
                    {faq.pregunta}
                  </p>
                  <p className="text-xs text-muted-foreground pl-6">
                    {faq.respuesta}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardPageLayout>
  );
}