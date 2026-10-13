import { useState } from 'react'
import { AlertTriangle } from 'lucide-react'
export default function ConfirmDialog({ appointment, onClose, onConfirm }) {
  const [deleting, setDeleting] = useState(false)
  async function confirm() { setDeleting(true); try { await onConfirm() } finally { setDeleting(false) } }
  return <div className="modal-backdrop" role="presentation"><section className="dialog confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="delete-title"><div className="confirm-icon"><AlertTriangle size={22} /></div><h2 id="delete-title">Delete appointment?</h2><p>This will permanently remove the appointment for <strong>{appointment.patient_name}</strong>.</p><div className="dialog-actions"><button className="button button-secondary" onClick={onClose} disabled={deleting}>Keep appointment</button><button className="button button-danger" onClick={confirm} disabled={deleting}>{deleting ? 'Deleting…' : 'Delete appointment'}</button></div></section></div>
}
