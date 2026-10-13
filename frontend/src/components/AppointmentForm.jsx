import { useEffect, useState } from 'react'
import { X } from 'lucide-react'

const doctors = ['Dr. Emily Carter', 'Dr. James Wilson', 'Dr. Sophia Anderson', 'Dr. Daniel Roberts', 'Dr. Olivia Martin']
const types = ['General Consultation', 'Follow-up', 'Dental Consultation', 'Specialist Consultation', 'Routine Check-up']
function toLocalInput(value) {
  const date = value ? new Date(value) : new Date()
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 16)
}
export default function AppointmentForm({ appointment, onClose, onSave }) {
  const [form, setForm] = useState({ patient_name: '', appointment_datetime: toLocalInput(), doctor: '', appointment_type: '', status: 'Scheduled' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  useEffect(() => {
    if (appointment) setForm({ patient_name: appointment.patient_name, appointment_datetime: toLocalInput(appointment.appointment_datetime), doctor: appointment.doctor, appointment_type: appointment.appointment_type, status: appointment.status })
  }, [appointment])
  function update(field, value) { setForm((current) => ({ ...current, [field]: value })) }
  async function submit(event) {
    event.preventDefault(); setError('')
    if (!form.patient_name.trim() || !form.appointment_datetime || !form.doctor || !form.appointment_type) { setError('Complete all required fields before saving.'); return }
    setSaving(true)
    try { await onSave({ ...form, patient_name: form.patient_name.trim(), appointment_datetime: `${form.appointment_datetime}:00` }) }
    catch (saveError) { setError(saveError.message) }
    finally { setSaving(false) }
  }
  return <div className="modal-backdrop" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && onClose()}><section className="dialog form-dialog" role="dialog" aria-modal="true" aria-labelledby="form-title">
    <div className="dialog-heading"><div><div className="eyebrow">APPOINTMENT DETAILS</div><h2 id="form-title">{appointment ? 'Edit appointment' : 'New appointment'}</h2><p>Enter the details for this clinic visit.</p></div><button className="icon-button" onClick={onClose} aria-label="Close form"><X size={19} /></button></div>
    <form onSubmit={submit}><label className="field-label">Patient name <span>*</span><input autoFocus maxLength="100" value={form.patient_name} onChange={(e) => update('patient_name', e.target.value)} placeholder="e.g. Alex Morgan" /></label>
      <div className="form-grid"><label className="field-label">Date <span>*</span><input type="date" value={form.appointment_datetime.slice(0, 10)} onChange={(e) => update('appointment_datetime', `${e.target.value}T${form.appointment_datetime.slice(11, 16) || '09:00'}`)} /></label><label className="field-label">Time <span>*</span><input type="time" value={form.appointment_datetime.slice(11, 16)} onChange={(e) => update('appointment_datetime', `${form.appointment_datetime.slice(0, 10)}T${e.target.value}`)} /></label></div>
      <label className="field-label">Doctor <span>*</span><select value={form.doctor} onChange={(e) => update('doctor', e.target.value)}><option value="">Select a doctor</option>{doctors.map((doctor) => <option key={doctor}>{doctor}</option>)}</select></label>
      <label className="field-label">Appointment type <span>*</span><select value={form.appointment_type} onChange={(e) => update('appointment_type', e.target.value)}><option value="">Select appointment type</option>{types.map((type) => <option key={type}>{type}</option>)}</select></label>
      {appointment && <label className="field-label">Status <span>*</span><select value={form.status} onChange={(e) => update('status', e.target.value)}>{['Scheduled', 'Completed', 'Cancelled'].map((status) => <option key={status}>{status}</option>)}</select></label>}
      {error && <div className="form-error" role="alert">{error}</div>}<div className="dialog-actions"><button type="button" className="button button-secondary" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={saving}>{saving ? 'Saving…' : appointment ? 'Save changes' : 'Create appointment'}</button></div>
    </form>
  </section></div>
}
