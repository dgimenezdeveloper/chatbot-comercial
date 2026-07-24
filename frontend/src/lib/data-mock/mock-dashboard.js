// Mock data for the dashboard panel page.
// Replace with real API calls when the backend endpoints are ready.

/** @typedef {'confirmed'|'pending_deposit'|'expired'|'unassigned'} AppointmentStatus */

/** @type {{ id: string, time: string, client: string, service: string, status: AppointmentStatus }[]} */
export const MOCK_TODAY_APPOINTMENTS = [
  { id: "1", time: "09:00", client: "Sofía Quintana",   service: "Coloración",        status: "confirmed"       },
  { id: "2", time: "10:30", client: "Facundo Torres",   service: "Corte de cabello",   status: "pending_deposit" },
  { id: "3", time: "12:00", client: "Ana García",       service: "Mechas",             status: "confirmed"       },
  { id: "4", time: "15:00", client: "(Sin Asignar)",    service: "Tratamiento",        status: "expired"         },
  { id: "5", time: "17:30", client: "Rodrigo López",    service: "Corte + Barba",      status: "confirmed"       },
];

/** @type {{ day: string, count: number }[]} */
export const MOCK_WEEKLY_SUMMARY = [
  { day: "Lunes",    count: 3  },
  { day: "Martes",   count: 5  },
  { day: "Miércoles",count: 8  },
  { day: "Jueves",   count: 9  },
  { day: "Viernes",  count: 8  },
  { day: "Sábado",   count: 9  },
];

export const MOCK_STATS = {
  todayAppointments: 8,
  depositsCobrados:  24500,
  botConsultas:      23,
  newClients:        3,
};
