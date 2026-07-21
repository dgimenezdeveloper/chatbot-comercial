# Documentación de Proyecto — Chatbot de Turnos

## Información de posibles escenarios

> Tres escenarios de medición distintos.

### Escenario 1 · El bot de agenda (el producto en sí)

**Bot de turnos — métricas internas del producto**
*Lo que mide el equipo para saber si el bot funciona y mejorar continuamente*

#### ⚡ Rendimiento del bot

| Métrica | Definición | Decisión |
|---|---|---|
| Tasa de resolución autónoma | % de conversaciones que el bot resolvió sin intervención humana | Si baja de 60% → el flujo tiene un problema o falta una intención |
| Tasa de fallback | % de mensajes que el bot no entendió sobre el total de mensajes recibidos | Si sube de 20% → revisar el NLU o agregar más intenciones |
| Tasa de escalamiento | % de conversaciones que terminaron en humano, separado por motivo | Si "2 fallbacks consecutivos" es el motivo principal → mejorar el flujo |
| Tiempo promedio hasta turno creado | Segundos desde `conversation_started` hasta `appointment_created` | Si supera 3 min → hay fricción en algún paso del flujo |
| Paso de abandono | En qué estado del flujo el usuario deja de responder sin completar | Si muchos abandonan en "selección de servicio" → el catálogo es confuso |

#### 🏢 Impacto en el negocio del cliente

| Métrica | Definición | Decisión |
|---|---|---|
| % turnos creados por el bot | De todos los turnos del mes, cuántos los inició el bot vs el dueño manualmente | Este número es el argumento de renovación del contrato del cliente |
| % turnos fuera de horario | Turnos reservados entre 20hs y 8hs — ventas que sin el bot se perdían | Es el KPI de propuesta de valor, no de rendimiento técnico |
| Tasa de no-show | Turnos que no asistieron / total de turnos confirmados | Si sube → evaluar recordatorio más agresivo o confirmación doble |
| Tasa de confirmación del recordatorio | De los recordatorios T-24hs enviados, cuántos recibieron respuesta positiva | Si baja de 50% → cambiar mensaje o timing del recordatorio |
| Horas pico de consultas | Distribución de conversaciones por hora del día y día de semana | Le ayuda al cliente a saber cuándo estar disponible para escalar |

#### 😊 Satisfacción y mejora continua

| Métrica | Definición | Decisión |
|---|---|---|
| CSAT promedio | Score 1–5 al final de la conversación, segmentado por resultado | CSAT bajo en conversaciones sin turno → el fallback frustra al usuario |
| Top mensajes con fallback | Los textos exactos que más veces no entendió el bot, agrupados por similitud | Esta lista es el roadmap del bot — cada grupo es una intención a agregar |
| Servicios más consultados | Qué servicios pregunta más la gente, aunque no siempre saquen turno | Insumo para que el cliente decida qué promover o qué precio revisar |

**Funnel de conversación — ejemplo con datos ilustrativos**

| Paso | Cantidad | % |
|---|---|---|
| Conversaciones iniciadas | 100 | 100% |
| Llegaron al menú principal | 78 | 78% |
| Eligieron "sacar turno" | 61 | 61% |
| Completaron selección de servicio | 48 | 48% |
| Seleccionaron fecha y hora | 44 | 44% |
| Turno confirmado | 38 | 38% |

---

### Escenario 2 · La web de ventas del producto (para conseguir clientes)

**Web de ventas — métricas de adquisición y conversión**
*Lo que mide el equipo para conseguir más clientes y mejorar el mensaje comercial*

#### 👥 Tráfico y adquisición

| Métrica | Definición | Decisión |
|---|---|---|
| Sesiones por canal | Orgánico, redes sociales, directo, referido, email — de dónde viene cada visita | Dónde invertir tiempo de marketing según qué canal convierte más |
| Nuevos vs recurrentes | % de visitantes que nunca habían entrado vs los que vuelven | Si muchos vuelven sin convertir → el mensaje de conversión falla |
| Término de búsqueda de entrada | Con qué palabras llegan los prospectos desde Google | Si llegan por "chatbot para negocios" y la web habla de "automatización" → hay desconexión |
| Tasa de rebote por página de entrada | % que entra y se va sin interactuar, por landing | Si rebota más del 70% → el mensaje inicial no resuena con la audiencia |

#### 🔍 Comportamiento en la web

| Métrica | Definición | Decisión |
|---|---|---|
| Scroll depth en la landing | Hasta dónde llegan los usuarios antes de irse o convertir | Si nadie llega al bloque de precios → el contenido previo no los engancha |
| Clicks en el demo / prueba gratis | CTR del CTA principal — el botón más importante de la web | Si el tráfico es alto pero el CTR bajo → cambiar el copy del CTA |
| Tiempo en página de precios | Cuánto tiempo pasan en la página de planes antes de decidir | Muy corto, no leyeron / no entendieron el valor. Muy largo, dudan |
| Heatmap de clicks y scroll | Dónde hace clic la gente, qué ignoran, qué los atrae visualmente | Si clickean en algo que no es un link → agregar ese link |
| Reproducción del video demo | % que reproduce el video, hasta dónde llegan, en qué segundo abandonan | Si abandonan en el segundo 10 → los primeros 10 segundos no convencen |

#### 🎯 Conversión y calificación de leads

| Métrica | Definición | Decisión |
|---|---|---|
| Tasa de conversión visita → lead | % de visitas que dejan su contacto (formulario, WhatsApp, demo) | Benchmark SaaS: 2–5% es razonable. Menos → revisar propuesta de valor |
| Tasa de conversión lead → cliente | De los que dejaron contacto, cuántos terminaron pagando | Si es baja → el problema está en el proceso de venta, no en la web |
| Rubro del lead | Si el formulario pregunta el tipo de negocio, segmentar leads por rubro | Si vienen peluquerías pero querés bazar → revisar el mensaje o el canal |
| CAC por canal | Costo de adquisición dividido por canal de origen del lead | Invertir más en el canal con menor CAC y mayor LTV |
| Tiempo hasta primer contacto | Cuántas horas pasan entre que deja el contacto y alguien del equipo lo llama | Más de 2hs reduce la tasa de cierre a la mitad — es urgente |

#### 🔄 Retención y expansión

| Métrica | Definición |
|---|---|
| Churn mensual | % de clientes que cancelaron el servicio ese mes. El número más importante del negocio. Arriba de 8% mensual es alarma crítica |
| NPS de clientes activos | ¿Recomendarían el producto? Mide lealtad, no solo satisfacción. NPS bajo → antes de escalar ventas, hay que mejorar el producto |
| Tasa de referidos | % de nuevos clientes que vienen por recomendación de uno existente. Si es alta → invertir en programa de referidos formal antes que en ads |

---

### Escenario 3 · Bot implementado en cliente — ecommerce o presupuestos

**Bot en cliente — métricas del negocio del cliente**
*Lo que el cliente puede ver en su panel para medir el impacto del bot en su negocio*

#### Si el cliente tiene ecommerce

**📊 Conversión comercial**

| Métrica | Definición |
|---|---|
| Consultas que derivaron en compra | De las conversaciones del bot, cuántas terminan en una orden en el ecommerce. Requiere conectar `session_id` del bot con `order_id` del ecommerce |
| Ticket promedio de compras bot-asistidas | ¿Compran más o menos los que pasaron por el bot vs los que no? Si es mayor → el bot ayuda a tomar decisiones más informadas |
| Tasa de abandono de carrito post-bot | Usuarios que el bot derivó al ecommerce pero no compraron. Si es alta → el bot deriva bien pero el ecommerce tiene fricción |
| Productos más consultados vs más comprados | Gap entre lo que la gente pregunta y lo que compra. Si algo se consulta mucho pero no se compra → precio, imagen o descripción falla |
| Ventas recuperadas fuera de horario | Órdenes generadas entre 20hs y 8hs donde el bot fue el primer contacto. Es el KPI de propuesta de valor más claro para renovar el contrato |
| Tasa de recompra de clientes bot-asistidos | ¿Los que compraron vía bot vuelven más que los que compraron directo? Si es mayor → el bot genera mejor experiencia de compra |

**🔎 Inteligencia de catálogo**

| Métrica | Definición |
|---|---|
| Top productos consultados | Ranking de los productos que más preguntaron, independiente de compra. Insumo de reposición de stock y decisiones de merchandising |
| Búsquedas sin resultado | Productos que buscaron y no estaban en el catálogo. Oportunidad de expansión de catálogo — demanda no satisfecha |
| Preguntas de precio por producto | Qué productos generan más consultas de precio antes de decidir. Si un producto tiene muchas consultas de precio pero poca conversión → el precio frena |

#### Si el cliente genera presupuestos

**📋 Pipeline de presupuestos**

| Métrica | Definición |
|---|---|
| Presupuestos generados por bot | Cantidad de presupuestos que el bot armó sin intervención del vendedor. Mide el ahorro de tiempo del equipo comercial |
| Tasa de conversión presupuesto → venta | De los presupuestos enviados por el bot, cuántos se cerraron. Si es baja → el presupuesto automático no tiene suficiente información o personalización |
| Tiempo desde consulta hasta presupuesto | Minutos entre que el usuario pregunta y recibe el presupuesto. El argumento de ventas más fuerte: "antes tardaba 24hs, ahora 3 minutos" |
| Presupuestos con datos incompletos | Presupuestos que el bot no pudo completar y derivó a humano. Decisión: qué información falta capturar en el flujo de preguntas |
| Valor promedio de presupuesto bot vs manual | ¿El bot genera presupuestos de menor o mayor valor que el vendedor humano? Si es menor → el bot no sabe hacer upselling o le faltan opciones |
| Motivo de rechazo de presupuesto | Precio, plazo, producto incorrecto, sin respuesta. Requiere follow-up manual, pero el bot puede preguntar "¿por qué no te convenció?" |

**🧑 Calidad del lead calificado**

| Métrica | Definición |
|---|---|
| Score de calificación del lead | El bot puede preguntar: volumen, urgencia, presupuesto disponible. Eso genera un score que permite que el vendedor priorice los leads calientes automáticamente |
| Leads derivados a humano con contexto | % de escalamientos donde el bot pasó un resumen de la consulta al vendedor. Si el vendedor recibe contexto → el tiempo de cierre baja significativamente |

---

### La métrica que conecta los tres escenarios

**ROI del bot por cliente — el número que justifica todo**

| Cálculo | Fórmula | Nota |
|---|---|---|
| Tiempo ahorrado por mes | `(consultas_bot × tiempo_promedio_manual) / 60` | En horas. El dueño lo valora en plata |
| Ventas nocturnas recuperadas | `turnos_nocturnos × ticket_promedio` | El argumento de renovación más fuerte |
| ROI del bot | `(valor_generado − costo_bot) / costo_bot` | Si es >3x → el cliente renueva solo |

> El ROI del bot es la métrica que conecta el escenario 1 (el producto funciona), el escenario 2 (el cliente lo compró porque vio el caso de éxito) y el escenario 3 (el cliente renueva porque lo midió). Si data no instrumenta esto desde el día 1, el equipo de ventas no tiene argumento para cerrar ni para retener.

---

## Posibles métricas

### Caso de uso 1: agendar turno nuevo

**🗓️ El usuario quiere reservar un turno**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Tasa de conversión inicio → turno | De todas las personas que abren el bot, cuántas terminan reservando un turno | `turnos_creados / conversations_iniciadas` | Métrica base: ¿funciona el bot? Sin esto, no sabés nada | Crítico |
| Tasa de conversión por servicio | Para cada servicio, cuántos terminan reservando vs consultan sin agendar | `turnos_servicio_X / consultas_servicio_X` | Hay servicios que venden solos, otros que pierden clientes. ¿Por qué? | Segmentación |
| Tiempo promedio para crear turno | Desde primer mensaje hasta confirmación: cuántos segundos tarda | `AVG(appointment_created_timestamp - conversation_start_timestamp)` | Si sube de 3min a 10min, hay fricción. ¿Dónde está? | UX |
| Tasa de abandono por paso del flujo | En qué paso pierde más usuarios (si lo saben): selección servicio, fecha, hora, confirmación | `usuarios_que_llegaron_a_paso_X_pero_no_avanzaron / usuarios_que_llegaron_a_paso_X` | El cuello de botella está en un paso específico, no es todo igual | Crítico |
| Tasa de reintentos tras fallback | El bot no entiende algo. El usuario reintenta o abandona | `usuarios_que_reintentan_tras_fallback / usuarios_con_fallback` | Fallback bajo confianza es recuperable. Fallback alto es pérdida | UX |
| % turnos nocturnos (20hs–8hs) | De los turnos creados, cuántos se reservaron fuera de horario comercial | `turnos_creados_entre_20y8 / total_turnos_creados` | El argumento de venta #1: "vendemos de noche". Sin este dato, es solo publicidad | Crítico |
| % turnos por anticipación | Cuántos se reservan para hoy, mañana, próxima semana, mes que viene | `COUNT(*)` agrupado por `(scheduled_date - today)` | Clientes que planifican vs de urgencia. Demanda predecible vs impredecible | Planning |
| Distribución de horarios preferidos | A qué hora del día reservan los turnos: 9am, 12pm, 3pm, 7pm, etc | `COUNT(*)` agrupado por `EXTRACT(HOUR FROM scheduled_at)` | Capacidad: si todos quieren las 6pm, el negocio no puede cumplir | Capacity |
| Servicios más reservados | Ranking de servicios por volumen de turnos | `COUNT(*)` agrupado por `service_id`, ordenado DESC | ¿Todos piden lo mismo o hay variedad? Impacta en inventario y staff | Business |
| Clientes nuevos vs recurrentes | De los turnos creados, cuántos son usuarios que nunca usaron el bot | `first_appointment / total_appointments` | Adquisición vs retención. Si baja de 50% a 20%, hay churn | Retention |

### Caso de uso 2: modificar turno existente

**🔧 El usuario quiere cambiar fecha/hora de un turno**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Tasa de self-service en modificaciones | De los cambios de turno, cuántos se hicieron completamente vía bot sin humano | `modificaciones_exitosas_via_bot / total_intentos_modificacion` | Si baja mucho, el flujo de búsqueda de turno no funciona | Crítico |
| Motivos de cambio (por intención) | Qué hace que remodifiquen: "se me olvidó", "necesito otro día", "otro horario" | Clustering de mensajes con intención "modificar" | Identifica si hay un problema sistemático (ej: horarios muy ocupados) | Insights |
| Modificaciones después de recordatorio | De las personas que recibieron recordatorio, cuántas querían cambiar de hora | `modificaciones_iniciadas_post_reminder / reminders_enviados` | El recordatorio dispara cambios de planes. Oportunidad para proponer slots alternativos | Trigger |
| Tiempo promedio entre turno original y modificación | Cuándo se arrepienten: mismo día, día antes, semana antes | `AVG(modification_date - original_appointment_date)` | Si modifican 1 hora antes, pueden perder slot. Si modifican 1 semana antes, hay más opciones | Planning |

### Caso de uso 3: cancelar turno

**❌ El usuario quiere cancelar un turno**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Tasa de cancelación | De todos los turnos creados, qué % se cancela antes de que ocurra | `cancelled_appointments / total_appointments` | Si baja de 15% a 5% es ganancia real. Si sube a 30% hay problema | Crítico |
| Cancelación tardía (últimas 24hs) | De las cancelaciones, cuántas ocurren menos de 24hs antes del turno | `cancelled_appointments_<24h_antes / total_cancelled` | Impacto en el negocio: no puede llenar ese slot. Pérdida directa | Business |
| Motivos de cancelación (texto original) | Qué escriben los usuarios cuando cancelan: "No puedo", "Cambio de planes", "Otro lugar" | Clustering del texto de cancelación | Identifica si hay un problema que se puede resolver (ej: horarios limitados) | Insights |
| Cancelaciones post-recordatorio | El recordatorio T-24hs, ¿dispara cancelaciones? | `cancellations_within_4h_after_reminder / total_reminders` | Si sube mucho, el recordatorio es contraproducente o el timing es malo | Trigger |

### Caso de uso 4: recordatorio automático T-24hs

> **Nota:** por WhatsApp es pago el envío de recordatorios por fuera de la ventana de 24 horas. Si está fuera de la ventana, será necesario disparar un medio alternativo.

**⏰ El bot manda recordatorio automático**

- **Tasa de envío exitoso**
  - *Definición:* de los turnos con T-24hs, cuántos reciben el recordatorio sin error.
  - *Cálculo:* `reminders_sent_successfully / total_reminders_scheduled`
  - *Nota:* si baja mucho, hay problema técnico de WhatsApp. Si no está dentro de la ventana, hay que buscar medio alternativo de envío.
  - *Categoría:* Technical

- **Tasa de lectura del recordatorio (read receipt)**
  - *Definición:* de los recordatorios enviados, cuántos fueron leídos en WhatsApp.
  - *Cálculo:* `messages_read / messages_sent`
  - *Nota:* si <50%, el recordatorio se pierde en el ruido. Si >80%, llega bien.
  - *Categoría:* Engagement

- **Tasa de respuesta al recordatorio**
  - *Definición:* de los recordatorios leídos, cuántos generan una respuesta.
  - *Cálculo:* `responses_to_reminder / reminders_read`
  - *Nota:* si <30%, la gente lo lee pero no interactúa. Mensaje poco enganchante.
  - *Categoría:* Engagement

- **Tasa de confirmación de asistencia**
  - *Definición:* del recordatorio, cuántos responden "confirmo".
  - *Cálculo:* `confirm_responses / reminders_sent`
  - *Nota:* si baja de 60%, hay incertidumbre. El negocio no sabe quién viene.
  - *Categoría:* Critical

- **Tiempo promedio de respuesta al recordatorio**
  - *Definición:* cuánto tardan en responder desde que reciben el recordatorio.
  - *Cálculo:* `AVG(response_time) post reminder`
  - *Nota:* si tardan horas, no es confirmación en vivo. Si responden en 10min, es real.
  - *Categoría:* Behavior

- **Impacto en no-shows**
  - *Definición:* turnos con confirmación de recordatorio que no asistieron vs sin confirmar.
  - *Cálculo:* `(no_show_confirmed / total_confirmed)` vs `(no_show_unconfirmed / total_unconfirmed)`
  - *Nota:* ¿el recordatorio reduce realmente el no-show? Si no, parar de enviarlo.
  - *Categoría:* Business

- **Impacto en tasa de cancelación por no confirmación.**

### Caso de uso 5: consultar disponibilidad sin agendar

**🔍 El usuario "mira" pero no reserva**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Consultas sin conversión | Usuarios que consultan disponibilidad pero no reservan nada | `availability_queries - completed_appointments` | Hay fricción entre mirar y agendar. ¿Es el precio? ¿No hay hora que les sirva? | Friction |
| Horarios más consultados sin resultado | Qué slots miran pero no hay disponibilidad | `COUNT(*)` por slot solicitado, filtrando "sin disponibilidad" | Si todos quieren viernes a las 6pm y nunca hay, el negocio necesita escalar | Capacity |

### Caso de uso 6: consultar precios

**💰 El usuario quiere saber cuánto cuesta**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Consultas de precio por servicio | Qué servicios los usuarios preguntan el precio antes de agendar | `COUNT(*)` de `intent="consultar_precio"` agrupado por `service_id` | Servicios premium generan dudas. Oportunidad para justificar el precio | Pricing |
| Tasa de conversión post-consulta de precio | De quienes consultan precio, cuántos terminan agendando | `bookings_after_price_query / price_queries` | Si <40%, el precio es una barrera. Necesitás comunicación diferente | Conversion |

### Caso de uso 7: consultar profesionales/empleados

**🙋 El usuario quiere saber quién lo va a atender**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Preferencia de profesional | Cuántos usuarios especifican o preguntan por un profesional en particular | `COUNT(*)` de mentions de `professional_id` / `total_bookings` | Hay profesionales que "venden" solos. Otros con menos demanda | Business |
| Impacto en conversión por profesional | Turnos reservados con cada profesional vs sin especificar | `bookings_prof_A / available_slots_prof_A` vs `turnos_sin_profesional` | ¿Atraer un profesional nuevo genera conversiones o solo redistribuye demanda? | Business |

### Caso de uso 8: interacción bot vs escalamiento a humano

**🙅 El bot no entiende o el usuario quiere hablar con alguien**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Tasa de resolución autónoma (IA) | De todas las conversaciones, cuántas se resuelven sin intervención humana | `(appointments_created + queries_resolved) / total_conversations` | ROI del bot. Si <50%, los costos de servidor no se justifican | Crítico |
| Tasa de fallback (no entiende) | % de mensajes donde el bot dice "no entendí" y pide aclaración | `fallback_messages / total_messages` | Si baja de 15%, el NLU mejora. Si sube de 25%, necesita reentrenamiento | Quality |
| Top 10 mensajes con fallback | Los textos exactos que más veces no entiende el bot | Ranking de `mensajes_fallback`, contando frecuencia | El roadmap del bot. Cada intención nueva aquí = +1 mejora de conversión | Crítico |
| Escalamiento manual (usuario solicita) | % de conversaciones donde el usuario dice "quiero hablar con alguien" | `escalation_requested / total_conversations` | Si es >30%, el bot no genera confianza. Rediseño necesario | UX |
| Escalamiento automático (2 fallbacks consecutivos) | Si el bot no entiende dos veces seguidas, escala automáticamente | `auto_escalations / total_conversations` | Mide cuándo el bot "se rinde". Si <5%, el flujo es claro. Si >20%, hay confusión | UX |
| Motivos de escalamiento | Por qué escalan: fallback repetido, queja, fuera de horario, otro servicio | Clustering de `escalation_reason` | Algunas razones se pueden automatizar. Otras no | Optimization |
| Tasa de conversión post-escalamiento | De los que escalaron a humano, cuántos terminan agendando | `bookings_after_human / total_escalations` | Si <50%, el humano no está cerrando bien. Si >80%, el bot está sacando leads buenos | Sales |

### Caso de uso 9: retención y re-engagement

**🔁 ¿Los usuarios vuelven a usar el bot?**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Usuarios recurrentes | De quienes usaron el bot una vez, cuántos vuelven en 30 días | `users_returning_30d / total_users` | Si <30%, el bot es un hit-and-run. Si >60%, hay stickiness | Retention |
| Frecuencia de uso (cohorte) | De los usuarios activos, cuántos usan el bot más de 1 vez por mes | `users_with_2+_appointments / total_users` | Usuarios de baja frecuencia vs alta frecuencia | Behavior |
| Churn por canal | De los usuarios que vinieron de Instagram, WhatsApp o Google, cuántos desaparecen | `churned_users_per_channel / acquired_users_per_channel` | Un canal trae gente que no vuelve. Otro trae usuarios "pegajosos" | Acquisition |
| Tiempo entre primer y segundo turno | Cuántos días pasan entre la primera y segunda reserva | `AVG(second_appointment_date - first_appointment_date)` | Si es 7 días = clientela de mantenimiento (pelo, maquillaje). Si 60 días = clientela casual | Business |

### Caso de uso 10: asistencia real al turno (No-Show)

**✅ ¿La gente realmente va al turno?**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Tasa de no-show general | De todos los turnos agendados, cuántos no asistieron | `no_show_appointments / total_appointments` | Pérdida directa. Si >15%, hay problema de confianza o comunicación | Crítico |
| No-show por tipo de usuario (bot vs manual) | ¿Los turnos creados por el bot tienen más no-shows que por humano? | `no_show_rate_bot vs no_show_rate_manual` | Si el bot tiene más no-show, hay percepción de "no es real" o fue impulsivo | Quality |
| Impacto del recordatorio en no-show | Turnos con recordatorio leído vs sin recordatorio | `no_show_rate (reminder_read=true)` vs `(reminder_read=false)` | ¿El recordatorio reduce no-shows? Si reduce <20%, para de enviarlo | Business |
| No-show por servicio | Algunos servicios tienen más no-show que otros | `no_show_rate` agrupado por `service_id` | Servicios "frívolos" tienen más no-show. Requieren confirmación más agresiva | Business |

### Caso de uso 11: WhatsApp específicamente

**💬 Comportamiento en el canal WhatsApp**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| Distribución horaria de mensajes | En qué horas del día la gente usa más el bot en WhatsApp | `COUNT(*)` por `EXTRACT(HOUR FROM created_at)` | Horarios pico = cuándo enviar recordatorios. Horarios valle = mantenimiento | Operations |
| Distribución por día de semana | ¿Viernes tiene más tráfico que lunes? | `COUNT(*)` por `EXTRACT(DOW FROM created_at)` | Demanda de turnos es desigual por día. Impacta en staffing | Capacity |
| Velocidad de respuesta del usuario en WA | Cuánto tardan típicamente en responder cada mensaje del bot | `PERCENTILE(response_time, 50)` y `PERCENTILE(response_time, 95)` | Si la mediana es 2min = flujo ágil. Si es 10min = fricción o baja engagement | UX |
| Tipo de input: botones vs texto libre | ¿Los usuarios usan los botones interactivos o escriben? | `button_clicks / total_inputs` | Si <20% botones = no los ven. Si >80% = interfaz clara | UX |
| Longitud promedio de mensajes | ¿Los usuarios escriben 2 palabras o párrafos? | `AVG(MESSAGE_LENGTH(user_messages))` | Mensajes cortos = confianza en el bot. Largos = explicaciones, dudas | Behavior |
| Read receipts en recordatorios | De los recordatorios enviados, cuántos fueron leídos en 1h, 4h, 24h | Lectura acumulada por bucket de tiempo | Si se lee rápido, el bot está "top of mind". Si se lee tarde o no se lee, perdido | Engagement |

### Caso de uso 12: satisfacción y NPS

**😊 ¿Qué piensan los usuarios del bot?**

| Métrica | Definición | Cálculo | Insight | Tag |
|---|---|---|---|---|
| CSAT después de cada transacción | Al final de la conversación, preguntar: "¿te ayudé?" (Sí/No o 1–5) | `SUM(satisfactory_responses) / total_csat_asked` | Métrica base de calidad. Si <70%, algo está mal | Crítico |
| CSAT por resultado | Satisfacción diferenciada: si reservó, si escaló o si abandonó | CSAT agrupado por `conversation_outcome` | Quiénes están felices: los que reservaron. Quiénes enojados: los que escalaron | Insights |
| NPS de los usuarios del bot | Después de la transacción: "¿recomendarías este bot?" (0–10) | `NPS = %Promotores(9-10) - %Detractores(0-6)` | Métrica de largo plazo. NPS>50 = producto ganador | Strategy |
| Comentarios libres en cierre | Preguntar: "¿algo que le cambiarías?" → clustering de respuestas | Frecuencia de feedback por categoría | Roadmap real, no suposiciones. La gente te dice qué mejorar | Product |

---

## Métricas priorizadas para chatbot de turnos — Plan de medición

**Total de mediciones posibles:** 60+ (ver documento exhaustivo)
- **Críticas (MVP):** 12 métricas
- **Recomendadas (primeros 3 meses):** 8 métricas adicionales
- **Futuras (después de 6 meses de datos):** 40+ análisis avanzados

### Críticas — implementar desde el día 1

Estas 12 métricas definen si el producto funciona. Sin ellas, no hay negocio.

| Métrica | Por qué | Cálculo | Umbral de alerta |
|---|---|---|---|
| Tasa de conversión (inicio → turno) | ¿Funciona el bot? | Turnos creados / Conversaciones iniciadas | < 20% |
| % turnos creados por bot | Argumento de venta #1 | Turnos vía bot / Total turnos | < 40% |
| Tasa de abandono por paso | Dónde pierde usuarios | Usuarios que no avanzan / Usuarios en paso | > 40% |
| Tasa de fallback | Calidad del NLU | Fallbacks / Total mensajes | > 25% |
| Top 10 mensajes con fallback | Roadmap del bot | Ranking de intenciones no entendidas | Cualquier cambio |
| % turnos nocturnos (20–8hs) | ROI: ¿vende de noche? | Turnos creados 20–8hs / Total | < 30% → no hay valor agregado |
| Tasa de resolución autónoma | ¿Necesita humano? | (Turnos + Consultas resueltas) / Total | < 50% |
| Tasa de cancelación | Pérdida de ingresos | Cancelados / Total turnos | > 20% |
| Tasa de no-show | Asistencia real | No-asistieron / Total turnos | > 15% |
| Tasa de confirmación de recordatorio | ¿Funciona el T-24hs? | Confirmaciones / Recordatorios enviados | < 50% |
| Servicios más reservados | ¿Diversidad o concentración? | Ranking por volumen | Accionable (stock/planning) |
| CSAT promedio | Satisfacción del usuario | Media de scores 1–5 post-conversación | < 3.5 |

### Recomendadas — primeros 3 meses

Estas 8 dan contexto y permiten primeras optimizaciones.

| Métrica | Por qué | Acción si baja |
|---|---|---|
| Tiempo promedio para crear turno | UX friction | Auditar flujo paso a paso |
| Consultas sin conversión | ¿Qué frena? | Analizar mensajes de clientes que no compran |
| Tasa de reintentos tras fallback | ¿Recuperable o pérdida? | Si <50%, fallback es terminal. Cambiar mensaje |
| Horarios pico de consultas | Capacity planning | Staffing en horarios pico |
| Clientes nuevos vs recurrentes | Adquisición vs retención | Si baja % nuevos, problema de churn |
| Read receipts en recordatorio | ¿Se ve el mensaje? | Si <70%, cambiar hora o formato del mensaje |
| Tasa de conversión post-escalamiento | ¿El humano cierra? | Si <50%, entrenar al equipo de soporte |
| Usuarios que vuelven en 30 días | Stickiness | Si <30%, el bot no resuelve necesidad recurrente |

### Futuras — después de 6 meses (cuando haya volumen)

Análisis avanzados que requieren datos históricos:

- Cohorte de retención semanal
- Predictores de conversión (qué pasos correlacionan con compra)
- Análisis de churn causality (por qué se van)
- Lifetime value por canal de adquisición
- Clustering automático de fallbacks (8 categorías en lugar de 200 textos únicos)
- NPS estratégico (recomendación)
- Análisis de sentimiento en comentarios libres

---

## Plan de implementación

### Sprint 1 (semanas 1–2): Infraestructura de eventos
- [ ] Definir esquema de tabla `events` con 15 campos base
- [ ] Tabla `sessions` para agrupar conversaciones
- [ ] Tabla `appointments` con campos de medición
- [ ] Tabla `fallback_log` para rastrear "no entiende"
- [ ] Backend dispara eventos en cada estado del bot
- [ ] Pipeline de ingesta → Data Warehouse

### Sprint 2–3 (semanas 3–6): Implementar críticas
- [ ] Dashboard con 12 métricas críticas (view diaria)
- [ ] Alertas automáticas cuando una métrica baja del umbral
- [ ] Reportes semanales para el PM/Product Owner

### Sprint 4+ (semanas 7+): Recomendadas + análisis
- [ ] Agregar 8 métricas recomendadas al dashboard
- [ ] Segmentación por servicio, profesional, canal
- [ ] Cohorte semanal de retención

---

## KPIs por rol

### Para el dueño de la peluquería
1. **% turnos creados por bot** — ¿Vale la pena? (Target: > 40%)
2. **% turnos nocturnos** — ¿Genera ventas nuevas? (Target: > 30%)
3. **Tasa no-show** — Pérdida de ingresos (Target: < 15%)
4. **Tasa de cancelación tardía** — Problemas de capacidad (Target: < 5%)

### Para el equipo de producto
1. **Tasa de conversión (inicio → turno)** — ¿Funciona? (Target: > 30%)
2. **Tasa de fallback** — Calidad NLU (Target: < 15%)
3. **Tasa de resolución autónoma** — ROI (Target: > 70%)
4. **CSAT promedio** — Satisfacción (Target: > 4.0/5)
5. **Top 10 fallbacks** — Roadmap priorizado

### Para el equipo de datos
Responsable de: ingesta limpia, pipeline sin pérdidas, reportes puntuales.

---

## Decisiones de diseño (sin flujo definido)

Estos eventos deben capturarse en cualquier flujo que se elija:

| Evento | Momento | Captura |
|---|---|---|
| `conversation_started` | Momento en que el usuario clickea/escribe su primer mensaje | canal, timestamp, es_nuevo_usuario |
| `menu_option_selected` | El usuario elige una opción | option_name, session_id |
| `service_selected` | El usuario confirma un servicio | service_id, confidence_score |
| `fallback_triggered` | El bot no entiende | mensaje_original, estado_previo, fallback_n |
| `appointment_created` | Turno confirmado | appointment_id, via_bot=true, duración_flujo_seg, horario_nocturno |
| `escalation_to_human` | La conversación escaló a humano | motivo, n_fallbacks_previos, estado_en_flujo |
| `csat_submitted` | El usuario califica la experiencia | score 1–5, resultado (turno/sin_turno/escalado) |
| `reminder_sent` | Envío saliente T-24hs | appointment_id, timestamp, canal |
| `reminder_response` | El usuario responde al recordatorio | response_type (confirmo/cancelo/cambio), timestamp |
| `conversation_closed` | La conversación termina | duracion_seg, n_mensajes, n_fallbacks, resultado_final |

### Lo que NO es necesario definir aún
- Flujo exacto del bot (lineal vs no-lineal, menú vs NLU puro, con/sin botones)
- Orquestación técnica (Node.js, Python, etc.)
- Integración WhatsApp (official API, Baileys, plugin)

> Todas las métricas funcionan independientemente del flujo que se elija.

---

## Checklist para la reunión

- [ ] Presentar las 12 métricas críticas
- [ ] Explicar por qué cada una importa
- [ ] Mostrar el umbral de alerta para cada una
- [ ] Proponer los 6–7 eventos base (`conversation_started`, `appointment_created`, etc.)
- [ ] Estimar esfuerzo: 1 semana en backend para instrumentar
- [ ] Decidir: ¿dashboard interno en Metabase / Looker / custom?
- [ ] Aprobar el plan de 4 sprints

---

## Referencia: eventos mínimos que backend tiene que emitir

Para capturar las 12 críticas, backend necesita emitir eventos en estos puntos:

1. Usuario abre el bot → `conversation_started`
2. Usuario elige una opción → `menu_option_selected` o `intent_detected`
3. Usuario selecciona un servicio → `service_selected`
4. El bot no entiende algo → `fallback_triggered`
5. Usuario confirma un turno → `appointment_created`
6. Usuario quiere hablar con humano o el bot escala → `escalation_to_human`
7. Fin de conversación → `conversation_closed`
8. Usuario responde CSAT → `csat_submitted`
9. Bot manda recordatorio T-24hs → `reminder_sent`
10. Usuario responde recordatorio → `reminder_response`

**Total de puntos de instrumentación: 10**

Cada evento necesita:
- `session_id` (para agrupar una conversación)
- `business_id` (multi-tenant)
- `timestamp` (con timezone)
- `channel` (whatsapp/web)
- Propiedades específicas (ej: `service_id` solo en `service_selected`)

---

## Cómo comunicar esto al equipo

- **Slide 1:** "Las métricas que importan son 12. Sin ellas, no sabés si el bot funciona."
- **Slide 2:** "Cada métrica necesita un evento. Backend tiene que emitir 10 eventos."
- **Slide 3:** "Estimación: 1 semana de backend. Retorno: datos reales."
- **Slide 4:** "Plan: Semana 1 infraestructura, Semana 2 dashboard, Semana 3+ análisis."

---

## Preguntas para resolver antes del desarrollo

1. **¿Cuál es el flujo?** (lineal, no-lineal, NLU, menú, híbrido)
   → No importa. Las métricas funcionan igual.

2. **¿WhatsApp Business API o solución casera?**
   → No importa. Los eventos se capturan igual.

3. **¿Recordatorio T-24hs obligatorio?**
   → Sí es importante. Sin eso, no se puede medir confirmación de asistencia.

4. **¿El negocio ya tiene historial de turnos, o se empieza de cero?**
   → Si tiene, migrar datos históricos al esquema de eventos desde el día 1.

5. **¿Cuántos turnos/día espera el negocio en el MVP?**
   → Impacta en el threshold de alertas. Pero se empieza con los valores generales.
