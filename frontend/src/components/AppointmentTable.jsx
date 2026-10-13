import { CalendarDays, Clock3, Pencil, Trash2 } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

const dateFormat = new Intl.DateTimeFormat(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
const timeFormat = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' })
export function formatDate(value) { return dateFormat.format(new Date(value)) }
export function formatTime(value) { return timeFormat.format(new Date(value)) }

export default function AppointmentTable({ appointments, onEdit, onDelete }) {
  if (!appointments.length) return <div className="empty-state"><div className="empty-icon"><CalendarDays size={23} /></div><h3>No appointments found</h3><p>Try changing your search or filters, or add a new appointment.</p></div>
  return <div className="table-wrap"><table><thead><tr><th>Patient</th><th>Date &amp; time</th><th>Doctor</th><th>Appointment type</th><th>Status</th><th><span className="sr-only">Actions</span></th></tr></thead>
    <tbody>{appointments.map((appointment) => <tr key={appointment.id}>
      <td><div className="patient-cell"><div className="patient-avatar">{appointment.patient_name.split(' ').map((part) => part[0]).slice(0, 2).join('').toUpperCase()}</div><span className="patient-name">{appointment.patient_name}</span></div></td>
      <td><div className="datetime-cell"><span><CalendarDays size={14} />{formatDate(appointment.appointment_datetime)}</span><span><Clock3 size={14} />{formatTime(appointment.appointment_datetime)}</span></div></td>
      <td><span className="doctor-name">{appointment.doctor}</span></td><td><span className="type-text">{appointment.appointment_type}</span></td><td><StatusBadge status={appointment.status} /></td>
      <td><div className="row-actions"><button aria-label={`Edit ${appointment.patient_name}`} onClick={() => onEdit(appointment)}><Pencil size={16} /></button><button className="delete-action" aria-label={`Delete ${appointment.patient_name}`} onClick={() => onDelete(appointment)}><Trash2 size={16} /></button></div></td>
    </tr>)}</tbody></table></div>
}
