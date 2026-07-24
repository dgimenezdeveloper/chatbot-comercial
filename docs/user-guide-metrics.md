# Chatbot Comercial — Guía para el Dueño del Negocio

> **Versión:** julio 2026 · **Lectura estimada:** 7 minutos

---

## 1. ¿Qué es y para qué sirve?

Imaginá que tenés un negocio — una peluquería, un consultorio, un taller — y querés que tus clientes puedan **agendar turnos por WhatsApp** sin que vos tengas que estar pendiente del teléfono.

Este chatbot hace exactamente eso:

- 🗓️ Tus clientes **agendan turnos** hablando por WhatsApp, como si chatearan con una persona
- ⏰ **Les llega un recordatorio automático** el día anterior al turno (se envía una vez al día a las 9 AM)
- ✅ Pueden **confirmar o cancelar** respondiendo al mensaje
- ⭐ Al terminar, **califican la atención** con 1 a 5 estrellas

**Vos no hacés nada.** El bot atiende solo, 24 horas, los 7 días de la semana.

---

## 2. ¿Qué información me da el chatbot?

El bot no solo atiende: también **te muestra cómo está funcionando tu negocio**. Podés ver cosas como:

| Categoría | Lo que podés saber |
|-----------|-------------------|
| 📅 **Agendamiento** | ¿Cuántos turnos se crearon? ¿Qué servicios se piden más? ¿En qué horarios? |
| ❌ **Cancelaciones** | ¿Cuántos cancelan? ¿A último momento? ¿Por qué motivo? |
| 👻 **No-show** | ¿Cuántos clientes no vienen? ¿Es peor sin recordatorio? |
| ⭐ **Satisfacción** | ¿Qué puntaje te ponen? ¿Te recomendarían a otros? |
| 🔁 **Recurrencia** | ¿Los clientes vuelven? ¿Cada cuánto? |
| 💬 **WhatsApp** | ¿A qué hora escriben más? ¿Qué tan rápido responde el bot? |
| 🤖 **Bot vs humano** | ¿El bot resuelve solo o deriva mucho a una persona? |

En total tenés **50 indicadores** para entender tu negocio. No hace falta mirarlos todos — vos elegís los que más te importan.

### Las 12 métricas clave (MVP)

Estas son las que definen si el bot funciona o no. Cada una tiene un **semáforo** automático:

| # | Métrica | ¿Qué mide? | ¿Cuándo preocuparse? |
|---|---------|-----------|---------------------|
| 1 | **Conversión inicio → turno** | De cada 100 personas que escriben, cuántas agendan | Menos de 20 de cada 100 |
| 2 | **Turnos creados por el bot** | ¿El bot agencia sola o necesitás ayudar? | Menos del 40% |
| 3 | **Abandono por paso** | ¿En qué paso del flujo se pierde la gente? | Más del 40% |
| 4 | **Fallback (no entiende)** | ¿Cada cuánto el bot no entiende un mensaje? | Más del 25% de los mensajes |
| 5 | **Top 10 mensajes no entendidos** | ¿Qué es lo que la gente pregunta y el bot no entiende? | Cualquier cambio sirve para mejorar |
| 6 | **Turnos nocturnos** | ¿Cuántos turnos se reservan fuera del horario comercial (20hs a 8hs)? | Menos del 30% — el bot no da valor agregado |
| 7 | **Resolución autónoma** | ¿El bot resuelve solo sin necesidad de humano? | Menos del 50% |
| 8 | **Cancelaciones** | ¿Cuántos turnos se cancelan? | Más del 20% |
| 9 | **No-show** | ¿Cuántos clientes no vienen al turno? | Más del 15% |
| 10 | **Confirmación de recordatorio** | ¿Cuántos confirman que van a venir? | Menos del 50% |
| 11 | **Servicios más reservados** | ¿Qué es lo que más pide la gente? | Para decidir stock y promociones |
| 12 | **CSAT promedio** | ¿Qué puntaje te ponen los clientes (1 a 5)? | Menos de 3.5 |

---

## 3. ¿Cómo funcionan los recordatorios?

Cada día a las **9 AM (hora de Buenos Aires)**, el sistema revisa los turnos del día siguiente y les envía un recordatorio automático. Así funciona:

```
🔍 El sistema revisa los turnos de MAÑANA (una vez al día, 9 AM)
              │
     ┌────────┴────────┐
     ▼                 ▼
  ¿Tiene los         ¿No tiene
  templates          templates
  pagos de Meta?     pagos?
     │                 │
     ▼                 ▼
  Se envía igual    ¿El cliente habló
  (sin límite de    en las últimas
  24 horas) ✅      24 horas?
                       │
               ┌───────┴───────┐
               ▼               ▼
             Sí habló        No habló
               │               │
               ▼               ▼
         Se envía por      ¿Hay otro canal
         WhatsApp ✅       (SMS o email)?
                               │
                       ┌───────┴───────┐
                       ▼               ▼
                     Sí hay          No hay nada
                       │               │
                       ▼               ▼
                 Se envía por      🔔 TE AVISA
                 SMS/email ✅      A VOS por WhatsApp
                                   con los datos del turno
```

**Resumen:** El sistema intenta por todos los medios avisarle al cliente. Si no hay forma, **te avisa a vos** para que lo contactes manualmente.

Cada intento queda registrado en el **historial de recordatorios**, así siempre sabés qué pasó con cada cliente.

---

## 4. ¿Qué significan los colores?

Cada indicador tiene un **semáforo** para que de un vistazo sepas si las cosas van bien o mal:

| Color | Significado | Ejemplo |
|-------|------------|---------|
| 🟢 **Verde (OK)** | Todo bien, dentro de lo esperado | CSAT 4.2 — los clientes están contentos |
| 🟡 **Amarillo (Atención)** | Ojo, está rozando el límite | Cancelaciones 28% — revisá por qué |
| 🔴 **Rojo (Crítico)** | Hay un problema, hay que actuar | No-show 40% — mucha gente no viene |

**Vos definís los límites.** Lo que para una peluquería es "normal", para un consultorio médico puede ser "preocupante". Cada negocio configura sus propios números a través del panel de administración.

---

## 5. Preguntas frecuentes

### ¿Necesito saber de computación para usar esto?

**No.** El chatbot funciona solo una vez configurado. Vos solo mirás los resultados y decidís. La parte técnica la maneja el equipo de desarrollo.

### ¿Cómo veo los indicadores de mi negocio?

Los indicadores se consultan a través del panel de administración. El equipo de desarrollo te da acceso y podés ver todas las métricas en tiempo real con sus semáforos de colores.

### ¿Cómo activo los recordatorios?

Vienen activados por defecto. El sistema revisa los turnos **una vez por día a las 9 AM** y envía los mensajes automáticamente a los clientes que tienen turno al día siguiente.

### ¿Cuánto cuesta?

El envío de recordatorios usa WhatsApp normal, que no tiene costo extra. Si querés usar **templates pagos de Meta** (recomendado porque eliminan la restricción de 24 horas), tiene un costo adicional que depende de tu plan con Meta.

### ¿Qué pasa si un cliente no recibe el recordatorio?

El sistema intenta **4 caminos distintos** antes de rendirse:
1. Template pago de Meta (sin límite de 24 horas)
2. WhatsApp normal (si el cliente escribió en las últimas 24 horas)
3. Canal alternativo como SMS o email (si está configurado)
4. Si fallan todos, **te avisa a tu WhatsApp** con los datos del turno (nombre del cliente, fecha, hora, servicio) para que vos lo contactes manualmente

### ¿Puedo cambiar los límites de alerta?

**Sí.** Cada negocio define qué considera "bien", "regular" o "mal" para cada indicador. Si no tocás nada, se usan valores recomendados que funcionan para la mayoría de los negocios.

### ¿Cómo sé a quiénes se les avisó?

Podés consultar el **historial de recordatorios**: te muestra cada cliente, cada turno, si se envió o falló, y por qué canal se mandó.

### ¿Qué datos necesito para empezar?

Solo dos cosas:
- **Tu número de WhatsApp de negocio** (el que usan tus clientes para escribirte)
- **Tus servicios y horarios** (qué ofrecés y cuándo)

El equipo de desarrollo se encarga del resto.

### ¿Qué son los umbrales configurables?

Cada negocio tiene valores distintos. Podés definir para cada métrica:
- Un valor **warning** (amarillo) — cuando empieza a preocupar
- Un valor **critical** (rojo) — cuando hay que actuar sí o sí

Por ejemplo, una peluquería puede aceptar 15% de no-show, mientras que un consultorio médico puede querer la alerta roja al 5%.

---

## 6. Glosario — Palabras que pueden aparecer

| Término | Qué significa |
|---------|--------------|
| **CSAT** | "Customer Satisfaction". El puntaje promedio que te ponen los clientes (1 a 5). Arriba de 4 = excelente, abajo de 3 = hay que revisar |
| **NPS** | "¿Me recomendarías?". % de clientes que te recomiendan menos % de los que no. Arriba de 50 es muy bueno |
| **No-show** | Cliente que tenía turno y no vino ni avisó |
| **Tasa de conversión** | De cada 100 personas que preguntan, cuántas agendan turno |
| **Escalamiento** | Cuando el bot no puede resolver y deriva a una persona |
| **Churn** | Clientes que dejaron de venir. Mide "abandono" |
| **Umbral** | El número límite que separa "bien" de "regular" y "mal". Cada negocio configura los suyos |
| **Umbral warning** | Valor amarillo — cuando la métrica empieza a preocupar |
| **Umbral critical** | Valor rojo — cuando hay que actuar urgente |
| **Read receipt** | La confirmación de WhatsApp de que el mensaje fue leído (doble tilde azul ✓✓) |
| **Ventana de 24h** | Regla de WhatsApp: solo podés escribirle a un cliente si él te habló en las últimas 24 horas |
| **Template de Meta** | Mensaje pre-aprobado por Meta que se puede enviar sin límite de 24 horas |

---

*¿Tenés dudas? Consultá con el equipo de desarrollo.*