import { useState } from 'react'
import { KeyRound, UserRound, X } from 'lucide-react'

export default function SettingsDialog({ user, onClose, onSave }) {
  const [username, setUsername] = useState(user.username)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    const trimmedUsername = username.trim()
    if (!trimmedUsername) return setError('Username is required.')
    if (newPassword && newPassword.length < 8) return setError('New password must be at least 8 characters.')
    if (newPassword && newPassword !== confirmPassword) return setError('New passwords do not match.')
    if (!newPassword && confirmPassword) return setError('Enter a new password before confirming it.')
    if (!currentPassword) return setError('Enter your current password to save account changes.')

    setSaving(true)
    try {
      await onSave({
        current_password: currentPassword,
        username: trimmedUsername,
        new_password: newPassword || null,
      })
    } catch (saveError) {
      setError(saveError.message)
    } finally {
      setSaving(false)
    }
  }

  return <div className="modal-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
    <section className="dialog settings-dialog" role="dialog" aria-modal="true" aria-labelledby="settings-title">
      <div className="dialog-heading"><div><div className="eyebrow">ACCOUNT</div><h2 id="settings-title">Account settings</h2><p>Update your username or password.</p></div><button className="icon-button" onClick={onClose} aria-label="Close settings"><X size={19} /></button></div>
      <form onSubmit={submit}>
        <label className="field-label"><div className="settings-label"><UserRound size={14} /> Username</div><input autoComplete="username" minLength="3" maxLength="40" pattern="[a-zA-Z0-9_-]+" required value={username} onChange={(event) => setUsername(event.target.value)} /></label>
        <div className="settings-section-title"><KeyRound size={14} /> Change password <span>Optional</span></div>
        <label className="field-label">New password<input autoComplete="new-password" type="password" minLength="8" maxLength="128" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} placeholder="At least 8 characters" /><small className="field-hint">Use at least 8 characters. Leave blank to keep your current password.</small></label>
        <label className="field-label">Confirm new password<input autoComplete="new-password" type="password" minLength="8" maxLength="128" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} placeholder="Re-enter new password" /></label>
        <label className="field-label">Current password <span>*</span><input autoComplete="current-password" type="password" required value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} placeholder="Required to save changes" /></label>
        {error && <div className="form-error" role="alert">{error}</div>}
        <div className="dialog-actions"><button type="button" className="button button-secondary" onClick={onClose}>Cancel</button><button className="button button-primary" disabled={saving}>{saving ? 'Saving…' : 'Save changes'}</button></div>
      </form>
    </section>
  </div>
}
