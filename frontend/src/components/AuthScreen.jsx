import { useState } from 'react'
import { HeartPulse, LockKeyhole, LogIn, UserRoundPlus } from 'lucide-react'
import { login, register } from '../services/appointmentService.js'

export default function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      const user = await (mode === 'login' ? login({ username, password }) : register({ username, password }))
      onAuthenticated(user)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setBusy(false)
    }
  }

  return <main className="auth-page"><section className="auth-card">
    <a className="brand auth-brand" href="#login"><span className="brand-mark"><HeartPulse size={23} strokeWidth={2.2} /></span><span>Medi<span>Care</span><small>CLINIC MANAGEMENT</small></span></a>
    <div className="auth-intro"><div className="auth-icon"><LockKeyhole size={20} /></div><h1>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1><p>{mode === 'login' ? 'Sign in to manage your appointments.' : 'Create a private workspace for your appointments.'}</p></div>
    <form className="auth-form" onSubmit={submit}>
      <label className="field-label">Username<input autoComplete="username" minLength="3" maxLength="40" pattern="[a-zA-Z0-9_-]+" required value={username} onChange={(event) => setUsername(event.target.value)} placeholder="Your username" /></label>
      <label className="field-label">Password<input autoComplete={mode === 'login' ? 'current-password' : 'new-password'} type="password" minLength="8" maxLength="128" required value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 8 characters" /></label>
      {error && <div className="form-error" role="alert">{error}</div>}
      <button className="button button-primary auth-submit" disabled={busy}>{mode === 'login' ? <LogIn size={16} /> : <UserRoundPlus size={16} />}{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
    </form>
    <p className="auth-switch">{mode === 'login' ? 'New to MediCare?' : 'Already have an account?'} <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>{mode === 'login' ? 'Create account' : 'Sign in'}</button></p>
    <div className="auth-footnote">Each account has its own appointment list and statistics.</div>
  </section></main>
}
